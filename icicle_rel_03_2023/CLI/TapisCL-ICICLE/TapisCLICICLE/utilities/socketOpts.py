import json
import selectors
try:
    from . import schemas
except:
    import utilities.schemas as schemas


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
    """
    behind the scenes, low level functions to handle the socket operations of the client-server model
    """
    async def json_receive_explicit_async(self, connection, loop):
        json_data = ""
        while True:
            try: 
                json_data = json_data + await loop.sock_recv(connection, 1024).decode('utf-8') 
                return json.loads(json_data) 
            except ValueError: # if json is invalid, keep going
                continue
            except BlockingIOError: # this is raised in the event that it tries to receive data when no data available due to non blocking
                continue

    def json_receive_explicit(self, connection):
        json_data = ""
        while True:
            try: 
                json_data = json_data + connection.recv(1024).decode('utf-8') 
                return json.loads(json_data) 
            except ValueError:
                continue
            except BlockingIOError:
                continue

    async def json_send_explicit_async(self, connection, loop, data):
        json_data = json.dumps(data)
        await loop.sock_send(connection, json_data.encode())
    
    def json_send_explicit(self, connection, data):
        json_data = json.dumps(data)
        connection.send(json_data.encode())

    async def schema_send_explicit_async(self, connection, loop, data):
        await self.json_send_explicit_async(connection, loop, data)

    def schema_send_explicit(self, connection, data):
        self.json_send_explicit(connection, data.dict())

    async def schema_unpack_explicit(self, connection, loop):
        data = await self.json_receive_explicit_async(connection, loop)
        schema_type = schema_types[data['schema_type']]
        return schema_type(**data)
        
    def schema_unpack_explicit(self, connection):
        data = self.json_receive_explicit(connection)
        schema_type = schema_types[data['schema_type']]
        return schema_type(**data)
