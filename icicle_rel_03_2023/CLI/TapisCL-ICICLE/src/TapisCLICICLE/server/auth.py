import time
import os 
import sys
import json


from tapipy.tapis import Tapis
from federatedTenantAuthAPI.get import get_client_code
import requests


from socketopts import schemas
from utilities import exceptions


class ServerSideAuth:
    def create_token_device_grant(self, device_code, client_id, client_key):
        response = requests.post(r"https://smartfoods.develop.tapis.io/v3/oauth2/tokens", json={"grant_type":"device_code", "device_code":device_code}, auth=(client_id, client_key))
        parsed_data = json.loads(response.content.decode())
        return parsed_data['result']['access_token']['access_token']
    
    async def password_grant(self, connection, username: str, password: str, link: str):
        start = time.time()
        try:
            t = Tapis(base_url=f"https://{link}",
                    username=username,
                    password=password)
            t.get_tokens()
        except Exception as e:
            self.logger.warning(e)
            raise ValueError(f"Invalid tapis auth credentials")
        
        self.username = username
        self.password = password
        self.t = t
        self.url = link
        self.access_token = self.t.access_token

        self.configure_decorators(self.username, self.password)
        self.update_credentials(t, username, password)

        self.logger.info(f"initiated in {time.time()-start}")

        return f"Successfully initialized tapis service on {self.url}"
    
    async def device_code_grant(self, link, connection, password=None):
        start = time.time()
        try:
            t = Tapis(base_url=f"https://{link}")
        except Exception as e:
            self.logger.warning(e)
            raise ValueError(f"Invalid uri")
        client_id = get_client_code(link)
        authentication_information = self.t.authenticator.generate_device_code(client_id=client_id)
        payload = schemas.AuthRequest(request_type='device_code',
                                      message={"message":"Go to to the URL and enter the user code to authenticate", 
                                               "url":authentication_information.verification_uri, 
                                               "user_code": authentication_information.user_code})
        connection.send(payload)
        token = self.create_token_device_grant(client_id=client_id, client_key=None, device_code=authentication_information.device_code)#t.authenticator.create_token(grant_type="device_code", device_code='y7NPZccnzMoTi2GRNCAIer86wk6YKJbixdlru3wC') # if needed, add a confirmation from client here to wait for entry of data
        self.t = Tapis(base_url=f"https://{link}",
                       access_token=token)
        self.username = self.t.authenticator.get_userinfo().username
        self.password = password
        self.url = link
        self.access_token = self.t.access_token
        self.logger.info(f"initiated in {time.time()-start}")

    async def federated_grant(self, link, connection, password=None):
        start = time.time()
        try:
            t = Tapis(base_url=f"https://{link}")
        except Exception as e:
            self.logger.warning(e)
            raise ValueError(f"Invalid uri")
        auth_link = rf"{link}/v3/oauth2/webapp"
        payload = schemas.AuthRequest(auth_request_type='federated',
                                      message={
                                          "message":"Go to the URL and enter your account information",
                                          "url":auth_link
                                            }, 
                                      request_content={
                                          "user_code":None
                                          })
        connection.send(payload)
        response_code = connection.receive()
        token = t.authenticator.create_token(grant_type="authorization_code", code=response_code.user_code)
        self.t = Tapis(
            base_url=f"https://{link}",
            access_token = token
            )
        self.logger.info(f"initiated in {time.time()-start}")

    async def password_grant_handshake(self, connection):
        startup_data = schemas.StartupData(initial = self.initial)
        await connection.send(startup_data)
        self.logger.info("send the initial status update")

        for attempt in range(1, 4):
            url: schemas.StartupData = await connection.receive()
            self.logger.info("received the link")
            try:
                #await self.run_command(connection, {'command':'switch_service', 'link':url.url, 'verbose':False})
                await self.aggregate_command_map['switch_service'](link=url.url, connection=connection, server=self, verbose=False)
                self.logger.info("Verification success")
                break
            except ValueError as e:
                login_failure_data = schemas.ResponseData(response_message = (str(e), attempt))
                await connection.send(login_failure_data)
                self.logger.warning(f"Verification failure, {e}")
                if attempt == 3:  
                    self.logger.error(
                        "Attempted verification too many times. Exiting")
                    raise ValueError("auth failure")
                continue


class AuthClientSide:
    def auth(self):
        while True:
            auth_type = str(input(f"Enter an auth type to login with from the list {self.AUTH_TYPES}: ")).lower()
            if auth_type not in self.AUTH_TYPES:
                print(f"The auth type must be in the list {self.AUTH_TYPES}")
                continue
            auth_type_request = schemas.AuthRequest(auth_type=auth_type)
            self.connection.send(auth_type_request)
            break
        required_auth_information: schemas.AuthRequest = self.connection.receive()
        while True:
            print(required_auth_information.message)
            if not required_auth_information.request_content:
                break
            if required_auth_information.error:
                print(required_auth_information.error)
            form_response = self.form_handler(required_auth_information.request_content)
            self.connection.send(form_response)
            required_auth_information: schemas.AuthRequest = self.connection.receive() # if there is an error, server will just send the same form again
        print("Authorization success!")
        return required_auth_information.request_content['username'], required_auth_information.request_content['url']
            

