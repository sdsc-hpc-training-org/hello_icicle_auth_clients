import time
import socket
import asyncio
import traceback
import typing
import os
import json

from tapipy.tapis import Tapis

from commands import commandMap, decorators
from utilities import logger, exceptions
from socketopts import schemas, socketOpts
from server import auth


class ServerConnection(socketOpts.ServerSocketOpts):
    """
    connection object to wrap around async reader and writer to make work easier
    """
    def __init__(self, name, reader, writer, connection_list, debug=False):
        super().__init__(name, debug=debug)
        self.name = name
        self.connection_list: list = connection_list
        self.reader: asyncio.StreamReader = reader
        self.writer: asyncio.StreamWriter = writer
        self.task: asyncio.Task = None
        self.status = "CLOSED"
        self.shutdown_message = schemas.ResponseData(message={'message':'Shutdown initiated, closing'}, exit_status=1)

    def set_status_device_authenticating(self):
        self.status = 'DEVICE_CODE_AUTH'

    def set_status_closed(self):
        self.status = 'CLOSED'

    def set_task(self, task: asyncio.Task):
        self.task = task
        self.status = 'OPEN'

    async def close(self, connection_list_lock: asyncio.Lock):
        self.logger.info('ATTEMPTING TO CLOSE')
        if self.status == 'OPEN':
            result = self.task.cancel()
            self.logger.info("successfully cancelled task")
            await self.send(self.shutdown_message)
            self.writer.close()
            await self.writer.wait_closed()
            self.status = 'CLOSED'
        elif self.status == 'DEVICE_CODE_AUTH': # only in the auth file
            await self.send(schemas.AuthRequest(error='cancelled authentication during device_code grant', auth_request_type='device_code'))
            self.writer.close()
            await self.writer.wait_closed()
        else:
            self.writer.close()
            await self.writer.wait_closed()
        async with connection_list_lock:
            self.connection_list.remove(self)
        print(self.connection_list)
        self.logger.info('SUCCESSFULLY CLOSED')


class Server(commandMap.AggregateCommandMap, logger.ServerLogger, decorators.DecoratorSetup, auth.ServerSideAuth):
    """
    Receives commands from the client and executes Tapis operations
    """
    SESSION_TIME = 5000
    debug=False
    def __init__(self, IP: str, PORT: int):
        super().__init__()
        self.initial = True
        self.running = True

        self.t = None
        self.url = None
        self.access_token = None
        self.username = None
        self.password = None
        self.auth_type = None

        self.__name__ = "Server"
        self.initialize_logger(self.__name__)
        # setting up socket server
        self.ip, self.port = IP, PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)

        self.end_time = time.time() + self.SESSION_TIME # start the countdown on the timeout

        self.connections_list: list[ServerConnection] = []

        self.server = None
        self.num_connections = 0

        self.connection_list_lock = asyncio.Lock()
        self.logger.info('initialization complete')

    async def close_connections(self):
        print([connection.status for connection in self.connections_list])
        return await asyncio.gather(*[connection.close(self.connection_list_lock) for connection in self.connections_list])

    async def close(self):
        await self.close_connections()
        self.server.close()
        raise exceptions.Shutdown()

    async def check_timeout(self):
        while self.running:
            if time.time() >= self.end_time:
                self.logger.info("Timeout, shutting down")
                self.running = False
                return 'server timed out'
            await asyncio.sleep(3)
    
    async def check_shutdown(self):
        while self.running:
            await asyncio.sleep(3)
        await self.close()
        self.logger.info("The server shutdown.")
        return None

    async def handshake(self, connection):
        self.logger.info("Handshake starting")
        if self.initial:  # if this is the first time in the session that the cli is connecting
            startup_data = schemas.StartupData(initial = self.initial)
            await connection.send(startup_data)
            await self.auth_startup(connection)
        else:
            startup_result = schemas.StartupData(initial = self.initial, username = self.username, url = self.url)
            await connection.send(startup_result)
        self.initial = False
        self.logger.info("Final connection data sent")

    async def accept(self, reader, writer):
        """
        accept connection request and initialize communication with the client
        """  
        self.num_connections += 1
        self.end_time = time.time() + self.SESSION_TIME
        connection = ServerConnection(f"CON-{self.num_connections}", reader=reader, writer=writer, connection_list=self.connections_list, debug=self.debug)
        ip, port = writer.transport.get_extra_info('socket').getsockname()
        self.logger.info("Received connection request")
        try:
            await self.handshake(connection)
        except exceptions.InvalidCredentialsReceived as e:
            self.logger.warning("invalid credentials entered too many times. Cancelling request")
            await connection.close(self.connection_list_lock)
            return
        except exceptions.ClientSideError as e:
            self.logger.warning(f"Encountered client side error during startup handshake. {e}")
            await connection.close(self.connection_list_lock)
            return
        except Exception as e:
            self.logger.warning(e)
            await connection.close(self.connection_list_lock)
            return
        self.logger.info("connection is running now")
        await connection.send(schemas.ResponseData(request_content={name:argument.json() for name, argument in self.arguments.items()}))
        
        setup_response: schemas.ResponseData = await connection.receive()
        if not setup_response.request_content['setup_success']:
            self.logger.warning(f"The setup of the connection {connection.name} failed")
            return

        loop = asyncio.get_event_loop()
        task: asyncio.Task = loop.create_task(self.receive_and_execute(connection))
        connection.set_task(task)
        print([connection.status for connection in self.connections_list])
        self.connections_list.append(connection)

    async def receive_and_execute(self, connection: ServerConnection):
        """
        receive and process commands
        """
        self.logger.info(f"{connection.name} is now running")
        while self.running:
            try:
                print("RECEIVING HERE")
                message = await connection.receive()
                if not self.running:
                    raise exceptions.Shutdown
                kwargs = message.request_content
                result = await self.run_command(connection, kwargs)
                response = schemas.ResponseData(message={"message":result}, url=self.url, active_username=self.username)
                self.end_time = time.time() + self.SESSION_TIME 
                await connection.send(response)
                self.logger.info(message.schema_type)
            except exceptions.ClientSideError as e:
                self.logger.warning(e)
                continue
            except (exceptions.TimeoutError, exceptions.Shutdown) as e:
                #error_response = schemas.ResponseData(error=str(e), url=self.url, active_username=self.username, exit_status=1)
                #await connection.send(error_response)
                self.logger.warning(str(e))
                self.running = False
                return
            except exceptions.Exit as e:
                self.logger.info("user exit initiated")
                error_response = schemas.ResponseData(error=str(e), exit_status=1, url=self.url, active_username=self.username)
                await connection.send(error_response)
                await connection.close()
                return
            except OSError:
                self.logger.info("connection was lost, waiting to reconnect")
                await connection.close()
            except asyncio.CancelledError:
                return 'task was cancelled'
            except (exceptions.CommandNotFoundError, exceptions.NoConfirmationError, exceptions.InvalidCredentialsReceived, Exception) as e:
                error_str = traceback.format_exc()
                error_response = schemas.ResponseData(error=str(e), url=self.url, active_username=self.username)
                await connection.send(error_response)
                self.logger.warning(f"{error_str}")
    
    async def main(self):
        self.server = await asyncio.start_server(self.accept, sock=self.sock)
        try:
            async with self.server:
                result = await asyncio.gather(self.server.serve_forever(), self.check_timeout(), self.check_shutdown(), return_exceptions=True)#, self.check_timeout(), return_exceptions=True)
                self.logger.info(str(result))
        except (KeyboardInterrupt, exceptions.Shutdown):
            self.running = False


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    server = Server(socket.gethostbyname('127.0.0.1', 30000)) 
    try:
        asyncio.run(server.main())
    finally:
        loop.close()
