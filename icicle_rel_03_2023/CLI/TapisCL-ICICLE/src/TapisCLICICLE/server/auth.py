import time
import os 
import sys
import json
import webbrowser
import base64
import traceback


from tapipy.tapis import Tapis
from tapipy import tapis
from federatedTenantAuthAPI.get import get_client_code
import requests
import pyperclip


from socketopts import schemas
from utilities import exceptions
from commands.arguments import argument



class ServerSideAuth:
    def create_token_device_grant(link, device_code, client_id):
        response = requests.post(f"https://{link}/v3/oauth2/tokens", json={"grant_type":"device_code", "device_code":device_code, "client_id":client_id})
        parsed_data = json.loads(response.content.decode())
        return parsed_data['result']['access_token']['access_token'], parsed_data['result']['refresh_token']['refresh_token']
    
    def get_tenant_uris(self):
        if not self.t:
            t = Tapis('https://tacc.tapis.io')
        else:
            t = self.t
        tenants = t.tenants.list_tenants()
        uri_list = list()
        for tenant in tenants:
            uri_list.append(tenant.base_url.split("//")[1])
        return uri_list
    
    async def password_grant(self, link: str, connection):
        start = time.time()
        username_password_request = schemas.AuthRequest(auth_request_type='password',
                                                        request_content={"username":argument.Argument('username', size_limit=(1, 100), arg_type='str_input'), "password":argument.Argument('password', arg_type='secure')},
                                                        message={"message":"enter your TACC username and password"})
        for attempt in range(1, 4):
            await connection.send(username_password_request)
            username_password_response = await connection.receive()
            username = username_password_response.request_content['username']
            password = username_password_response.request_content['password']
            try:
                self.t = Tapis(f"https://{link}",
                               username=username,
                               password=password)
                print(self.t.base_url)
                self.t.get_tokens()
                break
            except exceptions.ClientSideError as e:
                raise e
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
        self.url = link
        self.access_token = self.t.access_token

        self.logger.info(f"initiated in {time.time()-start}")

        return f"Successfully initialized tapis service on {self.url}"
    
    async def device_code_grant(self, link: str, connection):
        start = time.time()
        self.t = Tapis(f"https://{link}", resource_set='dev')
        client_id = get_client_code(link)
        if not client_id:
            raise exceptions.NoTenantClient(link)
        authentication_information = self.t.authenticator.generate_device_code(client_id=client_id)
        payload = schemas.AuthRequest(auth_request_type='device_code',
                                      message={"message":"Go to the URL if it doesnt open automatically and enter the user code to authenticate. Then click y when you enter the code\nUser code copied to clipboard", 
                                               "url":authentication_information.verification_uri, 
                                               "user_code": authentication_information.user_code},
                                      request_content={'Entered User Code':argument.Argument('Entered User Code', arg_type='confirmation')})
        await connection.send(payload)
        pyperclip.copy(authentication_information.user_code)
        webbrowser.open(authentication_information.verification_uri)
        confirmation = await connection.receive()
        if not confirmation.request_content['Entered User Code']:
            raise RuntimeError(f"User indicated that device code auth failed") # get rid of this feature and switch to polling
        start_time = time.time()
        while True:
            try:
                access_info = self.t.authenticator.create_token(grant_type="device_code", device_code=authentication_information.device_code, client_id=client_id)
                break
            except Exception as e:
                print(e)
                time.sleep(1)
                if time.time() - start_time > 60:
                    raise RuntimeError("Timeout while polling for authenticator token")

        self.t = Tapis(f"https://{link}",
                       access_token=access_info.access_token.access_token,
                       refresh_token=access_info.refresh_token.refresh_token,
                       resource_set="dev")
        
        self.username = self.t.authenticator.get_userinfo().username
        self.url = link
        self.access_token = self.t.access_token

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
                                          "access_token":argument.Argument('access_token', arg_type='str_input')
                                          })
        await connection.send(payload)
        webbrowser.open(auth_link)
        response_code_message: schemas.AuthRequest = await connection.receive()
        
        self.t = Tapis(f"https://{link}",
                       access_token=response_code_message.request_content['access_token'].strip())

        self.username = self.t.authenticator.get_userinfo().username
        self.url = link
        self.access_token = self.t.access_token

        self.logger.info(f"initiated in {time.time()-start}")

        return f"Successfully initialized tapis service on {self.url}"

    async def auth_startup(self, connection):
        session_auth_type_request = schemas.AuthRequest(request_content={"Tenant URI":argument.Argument('Tenant URI', arg_type='str_input', choices=self.get_tenant_uris()), "auth_type":argument.Argument('auth_type', choices=['password', 'device_code', 'federated'], arg_type='str_input')},
                                                        auth_request_type="requested",
                                                        message={"message":"Enter the URI of the Tapis tenant you wish to connect to, then select your auth type from the options below",
                                                                 "grant options":['password', 'device_code', 'federated']})
        while True:
            try:
                await connection.send(session_auth_type_request)
                session_auth_type_response: schemas.FormResponse = await connection.receive()
                auth_type = session_auth_type_response.request_content['auth_type']
                if auth_type not in ('password', 'device_code', 'federated'):
                    raise exceptions.InvalidCredentialsReceived()
                self.auth_type = auth_type
                link = session_auth_type_response.request_content['Tenant URI']
                self.t = Tapis(f"https://{link}")#, resource_set='dev')
                break
            except exceptions.InvalidCredentialsReceived:
                session_auth_type_request.error = "Invalid auth type received"
            except tapis.errors.BaseTapyException:
                session_auth_type_request.error = "Invalid tenant URI received, try again"

        if auth_type != "password":
            session_password_request = schemas.AuthRequest(auth_request_type=auth_type, request_content={"password":argument.Argument('password', arg_type='secure', size_limit=(6, 50))},
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
                    connection.set_status_device_authenticating()
                    await self.device_code_grant(link, connection)
                    connection.set_status_closed()
                else:
                    await self.password_grant(link, connection)
                break
            except (exceptions.ClientSideError, exceptions.InvalidCredentialsReceived, exceptions.NoTenantClient, RuntimeError) as e:
                raise e
            except Exception as e:
                error_str = traceback.format_exc()
                print(error_str)
                continue
        success_message = schemas.AuthRequest(auth_request_type="success", message={
            "message":f"Successfully authenticated with {auth_type} authentication",
            "username":self.username,
            "url":link})
        self.configure_decorators(self.username, self.password)
        self.update_credentials(self.t, self.username, self.password)
        await connection.send(success_message)
            

