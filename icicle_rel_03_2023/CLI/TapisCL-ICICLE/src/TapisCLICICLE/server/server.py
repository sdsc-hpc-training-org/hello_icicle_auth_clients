import sys
import time
import socket
import os
import asyncio
import traceback

from tapipy.tapis import Tapis

if __name__ != "__main__":
    from commands import commandMap, decorators
    from utilities import logger, exceptions
    from socketopts import schemas, socketOpts
    from server import auth
else:
    import commands.commandMap as commandMap


class ServerConnection(socketOpts.ServerSocketOpts):
    """
    connection object to wrap around async reader and writer to make work easier
    """
    def __init__(self, name, reader, writer, debug=False):
        super().__init__(name, debug=debug)
        self.name = name
        self.reader = reader
        self.writer = writer

    async def close(self):
        await self.reader.feed_eof()
        self.writer.close()
        await self.writer.wait_closed()
        

class Server(commandMap.AggregateCommandMap, logger.ServerLogger, decorators.DecoratorSetup, auth.ServerSideAuth):
    """
    Receives commands from the client and executes Tapis operations
    """
    SESSION_TIME = 1200
    def __init__(self, IP: str, PORT: int):
        super().__init__()
        self.initial = True

        self.t = None
        self.url = None
        self.access_token = None
        self.username = None
        self.password = None
        self.auth_type = None
        self.current_system = None
        self.pwd = None

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

        self.server = None
        self.num_connections = 0

        self.logger.info('initialization complete')

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
        connection = ServerConnection(f"CON-{self.num_connections}", reader=reader, writer=writer, debug=True)
        self.timeout_handler()
        ip, port= writer.transport.get_extra_info('socket').getsockname()
        if ip != socket.gethostbyname(socket.gethostname()):
            raise exceptions.UnauthorizedAccessError(ip)
        self.logger.info("Received connection request")
        try:
            await self.handshake(connection)
        except ValueError:
            self.logger.warning("invalid credentials entered too many times. Cancelling request")
            await connection.close()
            return

        self.logger.info("connection is running now")
        loop = asyncio.get_event_loop()
        await loop.create_task(self.receive_and_execute(connection))

    def timeout_handler(self):  
        """
        checks if the timeout has been exceeded
        """
        if time.time() > self.end_time: 
            raise exceptions.TimeoutError

    async def receive_and_execute(self, connection):
        """
        receive and process commands
        """
        while True:
            try:
                message = await connection.receive()
                self.timeout_handler()  
                kwargs = message.request_content
                result = await self.run_command(connection, kwargs)
                if self.current_system:
                    response = schemas.ResponseData(message={"message":result}, url=self.url, active_username=self.username, pwd=self.pwd, system=self.current_system)
                else:
                    response = schemas.ResponseData(message={"message":result}, url=self.url, active_username=self.username)
                self.end_time = time.time() + self.SESSION_TIME 
                await connection.send(response)
                self.logger.info(message.schema_type)
            except exceptions.ClientSideError as e:
                self.logger.warning(e)
                continue
            except (exceptions.TimeoutError, exceptions.Shutdown) as e:
                error_response = schemas.ResponseData(error=str(e), exit_status=1, url=self.url, active_username=self.username)
                await connection.send(error_response)
                self.logger.warning(str(e))
                self.server.close()
                loop = asyncio.get_event_loop()
                loop.stop()
                loop.close()
                sys.exit(0)
            except exceptions.Exit as e:
                self.logger.info("user exit initiated")
                error_response = schemas.ResponseData(error=str(e), exit_status=1, url=self.url, active_username=self.username)
                await connection.send(error_response)
                await connection.close()
                return
                #self.accept()  # wait for CLI to reconnect
            except OSError:
                self.logger.info("connection was lost, waiting to reconnect")
                await connection.close()
            except (exceptions.CommandNotFoundError, exceptions.NoConfirmationError, exceptions.InvalidCredentialsReceived, Exception) as e:
                error_str = traceback.format_exc()
                error_response = schemas.ResponseData(error=str(e), url=self.url, active_username=self.username)
                await connection.send(error_response)
                self.logger.warning(f"{error_str}")
    
    async def main(self):
        self.server = await asyncio.start_server(self.accept, sock=self.sock)
        try:
            async with self.server:
                await self.server.serve_forever()
        except KeyboardInterrupt:
            self.server.close()
            sys.exit(0)


if __name__ == '__main__':
    server = Server(socket.gethostbyname(socket.gethostname()), 30000)
    asyncio.run(server.main())
