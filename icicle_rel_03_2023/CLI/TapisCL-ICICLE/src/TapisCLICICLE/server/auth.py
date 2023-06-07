import time
import os 
import sys
import json
import webbrowser
import base64


from tapipy.tapis import Tapis
from tapipy import tapis
from federatedTenantAuthAPI.get import get_client_code
import requests


from socketopts import schemas
from utilities import exceptions


from commands import args


class ServerSideAuth:
    def create_token_device_grant(self, device_code, client_id, client_key):
        response = requests.post(r"https://smartfoods.develop.tapis.io/v3/oauth2/tokens", json={"grant_type":"device_code", "device_code":device_code}, auth=(client_id, client_key))
        parsed_data = json.loads(response.content.decode())
        return parsed_data['result']['access_token']['access_token']
    
    async def password_grant(self, link: str, connection):
        start = time.time()
        username_password_request = schemas.AuthRequest(auth_request_type='password',
                                                        request_content={"username":None, "password":None},
                                                        message={"message":"enter your TACC username and password"})
        for attempt in range(1, 4):
            await connection.send(username_password_request)
            username_password_response = await connection.receive()
            username = username_password_response.request_content['username']
            password = username_password_response.request_content['password']
            try:
                t = Tapis(base_url=f"https://{link}",
                        username=username,
                        password=password)
                t.get_tokens()
                break
            except Exception as e:
                if attempt > 3:
                    username_password_request.message = None
                    username_password_request.request_content = None
                    username_password_request.error = "All attempts used, exiting"
                    connection.send(username_password_request)
                    if self.initial:
                        await self.aggregate_command_map['shutdown']
                    raise exceptions.InvalidCredentialsReceived()

                username_password_request.error = f"Authentication failure, attempt {attempt} of 3"

        self.username = username
        self.password = password
        self.t = t
        self.url = link
        self.access_token = self.t.access_token

        self.configure_decorators(self.username, self.password)
        self.update_credentials(t, username, password)

        self.logger.info(f"initiated in {time.time()-start}")

        return f"Successfully initialized tapis service on {self.url}"
    
    async def device_code_grant(self, link: str, connection):
        start = time.time()
        t = Tapis(base_url=f"https://{link}")
        client_id = get_client_code(link)
        authentication_information = self.t.authenticator.generate_device_code(client_id=client_id)
        payload = schemas.AuthRequest(request_type='device_code',
                                      message={"message":"Go to to the URL if it doesnt open automatically and enter the user code to authenticate", 
                                               "url":authentication_information.verification_uri, 
                                               "user_code": authentication_information.user_code})
        
        await connection.send(payload)
        webbrowser.open(authentication_information.verification_uri)

        client_auth = base64.b64encode(f"{client_id}:{client_key}".encode()).decode()
        token = t.authenticator.create_token(grant_type="device_code", device_code=authentication_information.device_code, _tapis_headers={"Authorization": f"Basic {client_auth}"})

        self.t = Tapis(base_url=f"https://{link}",
                       access_token=token)
        self.username = self.t.authenticator.get_userinfo().username
        self.url = link
        self.access_token = self.t.access_token

        self.configure_decorators(self.username, self.password)
        self.update_credentials(t, self.username, self.password)

        self.logger.info(f"initiated in {time.time()-start}")

        return f"Successfully initialized tapis service on {self.url}"

    async def federated_grant(self, link, connection):
        start = time.time()
        auth_link = rf"https://{link}/v3/oauth2/webapp"
        payload = schemas.AuthRequest(auth_request_type='federated',
                                      message={
                                          "message":"Go to the URL if it doesnt open and enter your account information. Then enter the user code to this application",
                                          "url":auth_link
                                            }, 
                                      request_content={
                                          "user_code":None
                                          })
        await connection.send(payload)
        webbrowser.open(auth_link)
        response_code_message: schemas.AuthRequest = await connection.receive()
        self.t = Tapis(
            base_url=f"https://{link}",
            access_token = response_code_message.request_content['user_code'].strip()
            )
        print(self.t)
        self.username = self.t.authenticator.get_userinfo().username
        self.url = link
        self.access_token = self.t.access_token

        self.configure_decorators(self.username, self.password)
        self.update_credentials(self.t, self.username, self.password)

        self.logger.info(f"initiated in {time.time()-start}")

        return f"Successfully initialized tapis service on {self.url}"

    async def auth_startup(self, connection):
        session_auth_type_request = schemas.AuthRequest(request_content={"uri":None, "auth_type":None},
                                                        auth_request_type="requested",
                                                        message={"message":"Enter the URI of the Tapis tenant you wish to connect to, then select your auth type from the options below",
                                                                 "options":args.Args.argparser_args['auth']['kwargs']['choices']})
        while True:
            try:
                await connection.send(session_auth_type_request)
                session_auth_type_response: schemas.FormResponse = await connection.receive()
                auth_type = session_auth_type_response.request_content['auth_type']
                if auth_type not in ('password', 'device_code', 'federated'):
                    raise exceptions.InvalidCredentialsReceived()
                self.auth_type = auth_type
                link = session_auth_type_response.request_content['uri']
                Tapis(f"https://{link}")
                break
            except exceptions.InvalidCredentialsReceived:
                session_auth_type_request.error = "Invalid auth type received"
            except tapis.errors.BaseTapyException:
                session_auth_type_request.error = "Invalid tenant URI received, try again"

        if auth_type != "password":
            session_password_request = schemas.AuthRequest(auth_request_type=auth_type, request_content={"password":None},
                                                            message={"message":"Please create a session password. The password must be at least 6 characters long"})
            while True:
                await connection.send(session_password_request)
                session_password_response: schemas.FormResponse = await connection.receive()
                requested_password = session_password_response.request_content['password']
                if len(requested_password) >= 6:
                    self.password = requested_password
                    break
                session_password_request.error = "The password provided was too short, the password must be at least 6 characters!!!"
        
        while True:
            try:
                if auth_type == "federated":
                    await self.federated_grant(link, connection)
                elif auth_type == "device_code":
                    await self.device_code_grant(link, connection)
                else:
                    await self.password_grant(link, connection)
                break
            except exceptions.InvalidCredentialsReceived:
                raise exceptions.InvalidCredentialsReceived
            except Exception as e:
                continue
        success_message = schemas.AuthRequest(auth_request_type="success", message={
            "message":f"Successfully authenticated with {auth_type} authentication",
            "username":self.username,
            "url":link})
        self.configure_decorators(self.username, self.password)
        await connection.send(success_message)
            

