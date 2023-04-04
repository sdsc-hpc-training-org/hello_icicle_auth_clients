import socket
import json
from TypeEnforcement.type_enforcer import TypeEnforcer
import typing
import pydantic
try:
    from . import schemas
except:
    import schemas


schema_types: dict = {
        'CommandData':schemas.CommandData,
        'AuthData':schemas.AuthData,
        'StartupData':schemas.StartupData,
        'ResponseData':schemas.ResponseData,
        'FormRequest':schemas.FormRequest,
        'FormResponse':schemas.FormResponse,
        'AuthRequest':schemas.AuthRequest,
        'ConfirmationRequest':schemas.ConfirmationRequest
    }


class SocketOpts:
    def json_receive_explicit(self, connection):
        json_data = ""
        while True:
            try: #to handle long files, so that it continues to receive data and create a complete file
                json_data = json_data + connection.recv(1024).decode('utf-8') #formulate a full file. Combine sequential data streams to unpack
                return json.loads(json_data) #this is necessary whenever transporting any large amount of data over TCP streams
            except ValueError:
                continue
    
    def json_send_explicit(self, connection, data):
        json_data = json.dumps(data)
        connection.send(json_data.encode())

    def schema_unpack_explicit(self, connection):
        data = self.json_receive_explicit(connection)
        schema_type = schema_types[data['schema_type']]
        return schema_type(**data)

    def json_receive(self) -> str | list | dict: # Receive and unpack json 
        return self.json_receive_explicit(self.connection)
    
    def json_send(self, data: dict | list | str): # package data in json and send
        return self.json_send_explicit(self.connection, data)

    def schema_unpack(self):
        return self.schema_unpack_explicit(self.connection)