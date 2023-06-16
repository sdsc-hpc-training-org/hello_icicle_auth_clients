import json
import typing

import pydantic


try:
    from socketopts import schemas
    from utilities import logger, exceptions
except:
    from . import schemas
    from ..utilities import logger, exceptions


schema_types: dict = {
        'CommandData':schemas.CommandData,
        'StartupData':schemas.StartupData,
        'ResponseData':schemas.ResponseData,
        'FormRequest':schemas.FormRequest,
        'FormResponse':schemas.FormResponse,
        'AuthRequest':schemas.AuthRequest,
        'ConfirmationRequest':schemas.ConfirmationRequest
    }


class BaseSocketOpts(logger.ConnectionLogger):
    """
    behind the scenes, low level functions to handle the socket operations asynchronoously on the server
    """
    def __init__(self, name, debug=False):
        self.initialize_logger(f"{name} LOGGER")
        self.debug_state = debug

    def debug(self, operation: typing.Literal["SENDING", "RECEIVED", "WAITING"], message: str | typing.Type[schemas.BaseSchema]):
        if self.debug_state:
            if not isinstance(message, str):
                self.logger.info(f"""{operation}: {message.schema_type}
                                    MESSAGE CONTENT:{message.request_content}
                                    MESSAGE: {message.message}
                                    ERROR: {message.error}""")
            else:
                self.logger.info(message)


class ClientSocketOpts(BaseSocketOpts):
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

    def send(self, data: typing.Type[schemas.BaseSchema]):
        self.debug('SENDING', data)
        self.__json_send_explicit(self.connection, data.dict())

    def receive(self) -> typing.Type[schemas.BaseSchema]:
        self.debug("WAITING", "Awaiting message receive")
        data = self.__json_receive_explicit(self.connection)
        schema_type = schema_types[data['schema_type']]
        self.debug('RECEIVED', schema_type(**data))
        return schema_type(**data)


class ServerSocketOpts(BaseSocketOpts):
    """
    behind the scenes, low level functions to handle the socket operations asynchronoously on the server
    """
    def __init__(self, name, debug=False):
        super().__init__(name, debug=debug)
        self.system = ''
        self.pwd = ''

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

    async def send(self, data: typing.Type[schemas.BaseSchema]):
        if data.request_content:
            for key, value in data.request_content.items():
                if not isinstance(value, (str, list, tuple, bool, int, dict, set)) and value != None:
                    data.request_content[key] = value.json()
        self.debug('SENDING', data)
        data.pwd = self.pwd
        data.system = self.system
        json_data = json.dumps(data.dict())
        self.writer.write(json_data.encode())
        await self.writer.drain()

    async def receive(self):
        self.debug("WAITING", "Awaiting message receive")
        data = await self.__json_receive_explicit_async()
        schema_type = schema_types[data['schema_type']]
        formatted_data = schema_type(**data)
        self.debug('RECEIVED', formatted_data)
        if formatted_data.error:
            raise exceptions.ClientSideError(formatted_data.error)
        return formatted_data
    
