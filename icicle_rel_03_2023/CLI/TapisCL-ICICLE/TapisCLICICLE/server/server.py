import sys
from getpass import getpass
import time
import re
from tapipy.tapis import Tapis
import socket
import os
import logging
import typing
import asyncio
import traceback

try:
    from ..utilities import exceptions
    from ..utilities import logger
    from ..utilities import socketOpts as SO
    from ..utilities import killableThread
    from ..utilities import schemas
    from . import serverConnection
    from ..commands.query import neo4j, postgres
    from ..commands import baseCommand
    from ..commands import commandMap
    from ..utilities import decorators
except ImportError:
    import utilities.decorators as decorators
    import utilities.exceptions as exceptions
    import utilities.logger as logger
    import utilities.socketOpts as SO
    import utilities.killableThread as killableThread
    import utilities.schemas as schemas
    import server.serverConnection as serverConnection
    import commands.baseCommand as baseCommand
    import commands.commandMap as commandMap


class Server(commandMap.AggregateCommandMap, logger.ServerLogger, decorators.DecoratorSetup):
    """
    Receives commands from the client and executes Tapis operations
    """
    def __init__(self, IP: str, PORT: int):
        super().__init__()
        self.initial = True

        self.t = None
        self.url = None
        self.access_token = None
        self.username = None
        self.password = None

        self.__name__ = "Server"
        self.initialize_logger(self.__name__)
        # setting up socket server
        self.ip, self.port = IP, PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        self.end_time = time.time() + 300  # start the countdown on the timeout

        self.server = None

        self.logger.info('initialization complete')

    def switch_session(self, username: str, password, link: str, *args, **kwargs):
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
        # V3 Headers
        header_dat = {"X-Tapis-token": t.access_token.access_token,
                      "Content-Type": "application/json"}
        # create authenticator for tapis systems
        authenticator = t.access_token
        # extract the access token from the authenticator
        
        if 'win' in sys.platform:
            os.system(f"set JWT={self.access_token}")
        else: # unix based
            os.system(f"export JWT={self.access_token}")

        self.logger.info(f"initiated in {time.time()-start}")

        return f"Successfully initialized tapis service on {self.url}"

    async def handshake(self, connection):
        self.logger.info("Handshake starting")
        if self.initial:  # if this is the first time in the session that the cli is connecting
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
        else:
            self.configure_decorators(self.username, self.password)
        self.initial = False
        startup_result = schemas.StartupData(initial = self.initial, username = self.username, url = self.url)
        self.logger.info("Connection success")
        await connection.send(startup_result)
        self.logger.info("Final connection data sent")

    async def accept(self, reader, writer):
        """
        accept connection request and initialize communication with the client
        """  
        connection = serverConnection.ServerConnection(reader=reader, writer=writer)
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
                kwargs, exit_status = message.kwargs, message.exit_status
                result = await self.run_command(connection, kwargs)
                response = schemas.ResponseData(response_message = result, url = self.url, active_username = self.username)
                self.end_time = time.time() + 300 
                await connection.send(response)
                self.logger.info(message.schema_type)
            except (exceptions.TimeoutError, exceptions.Shutdown) as e:
                error_response = schemas.ResponseData(response_message = str(e), exit_status=1)
                await connection.send(error_response)
                self.logger.warning(str(e))
                self.server.close()
                loop = asyncio.get_event_loop()
                loop.stop()
                loop.close()
                sys.exit(0)
            except exceptions.Exit as e:
                self.logger.info("user exit initiated")
                error_response = schemas.ResponseData(response_message = str(e), exit_status=1)
                await connection.send(error_response)
                await connection.close()
                return
                #self.accept()  # wait for CLI to reconnect
            except OSError:
                self.logger.info("connection was lost, waiting to reconnect")
                await connection.close()
            except (exceptions.CommandNotFoundError, exceptions.NoConfirmationError, exceptions.InvalidCredentialsReceived, Exception) as e:
                error_str = traceback.format_exc()
                error_response = schemas.ResponseData(response_message = f"{str(e)}")
                await connection.send(error_response)
                self.logger.warning(f"{error_str}")
    
    async def main(self):
        self.server = await asyncio.start_server(self.accept, sock=self.sock)
        async with self.server:
            await self.server.serve_forever()


if __name__ == '__main__':
    server = Server(socket.gethostbyname(socket.gethostname()), 30000)
    asyncio.run(server.main())
