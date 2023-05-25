import json
import typing

import pydantic


try:
    from socketopts import schemas
except:
    from . import schemas


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


class ClientSocketOpts:
    """
    synchronous sockets to be used by clients
    """
    def __json_receive_explicit(self, connection):
        json_data = ""
        while True:
            try: 
                json_data = json_data + connection.recv(1024).decode('utf-8') 
                return json.loads(json_data) 
            except ValueError:
                continue
            except BlockingIOError:
                continue

    def __json_send_explicit(self, connection, data):
        json_data = json.dumps(data)
        connection.send(json_data.encode())

    def send(self, data):
        self.__json_send_explicit(self.connection, data.dict())

    def recveive(self):
        data = self.__json_receive_explicit(self.connection)
        schema_type = schema_types[data['schema_type']]
        return schema_type(**data)


class ServerSocketOpts:
    """
    behind the scenes, low level functions to handle the socket operations asynchronoously on the server
    """
    async def __json_receive_explicit_async(self):
        json_data = ""
        while True:
            try: 
                byte_buffer = await self.reader.read(n=1024)
                json_data += byte_buffer.decode()
                return json.loads(json_data) 
            except ValueError: # if json is invalid, keep going
                continue
            except BlockingIOError: # this is raised in the event that it tries to receive data when no data available due to non blocking
                continue

    async def send(self, data: typing.Type[pydantic.BaseModel]):
        json_data = json.dumps(data.dict())
        self.writer.write(json_data.encode())
        await self.writer.drain()

    async def receive(self):
        data = await self.__json_receive_explicit_async()
        schema_type = schema_types[data['schema_type']]
        return schema_type(**data)
    
