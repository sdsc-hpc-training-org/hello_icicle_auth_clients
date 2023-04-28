import sys
from getpass import getpass
import time
import re
from tapipy.tapis import Tapis
import socket
import os
import logging
import typing
import selectors
import traceback

try:
    from .utilities import exceptions
    from .utilities import socketOpts as SO
    from .utilities import helpers
    from .utilities import schemas
    from .commands import serverCommands as serverCommands
except:
    import utilities.exceptions as exceptions
    import utilities.socketOpts as SO
    import utilities.helpers as helpers
    import utilities.schemas as schemas
    import commands.serverCommands as serverCommands


class Server(SO.SocketOpts, helpers.OperationsHelper, helpers.DynamicHelpUtility, serverCommands.ServerCommands):
    """
    Receives commands from the client and executes Tapis operations
    """
    def __init__(self, IP: str, PORT: int):
        super().__init__()
        self.initial = True

        self.selector = selectors.DefaultSelector()
        # logger setup
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler(stream=sys.stdout)

        file_handler = logging.FileHandler(
            r'logs.log', mode='w')
        stream_handler.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)

        # set formats
        stream_format = logging.Formatter(
            '%(name)s - %(levelname)s - %(message)s')
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        stream_handler.setFormatter(stream_format)
        file_handler.setFormatter(file_format)

        # add the handlers
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)

        self.logger.disabled = False

        # setting up socket server
        self.ip, self.port = IP, PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        self.end_time = time.time() + 300  # start the countdown on the timeout

        self.connections_list = []  # initialize the connection variable

        self.logger.info('initialization complete')

    def accept(self):
        """
        accept connection request and initialize communication with the client
        """  
        connection, ip_port = self.sock.accept() 
        connection.setblocking(False)
        ip, port = ip_port
        if ip != socket.gethostbyname(socket.gethostname()):
            raise exceptions.UnauthorizedAccessError(ip)
        self.connections_list.append(connection)
        self.logger.info("Received connection request")

        if self.initial:  # if this is the first time in the session that the cli is connecting
            startup_data = schemas.StartupData(initial = self.initial)
            self.json_send_explicit(connection, startup_data.dict())
            self.logger.info("send the initial status update")

            for attempt in range(1, 4):
                url: schemas.StartupData = self.schema_unpack_explicit(connection).url
                self.logger.info("received the link")
                try:
                    auth_request = schemas.AuthRequest()
                    self.logger.info("send the auth request")
                    self.json_send_explicit(connection, auth_request.dict())
                    auth_data: schemas.AuthData = self.schema_unpack_explicit(connection)
                    username, password = auth_data.username, auth_data.password
                    self.tapis_init(link=url, username=username, password=password, connection=connection, initial_connection=True)
                    self.commands_initializer()
                    self.logger.info("Verification success")
                    break
                except Exception as e:
                    login_failure_data = schemas.ResponseData(response_message = (str(e), attempt))
                    self.json_send_explicit(connection, login_failure_data.dict())
                    self.logger.warning(f"Verification failure, {e}")
                    if attempt == 3:  
                        self.logger.error(
                            "Attempted verification too many times. Exiting")
                        return
                    continue
        else:
            self.configure_decorators(self.username, self.password)
        self.initial = False
        startup_result = schemas.StartupData(initial = self.initial, username = self.username, url = self.url)
        self.logger.info("Connection success")
        self.json_send_explicit(connection, startup_result.dict())
        self.logger.info("Final connection data sent")
        self.selector.register(connection, selectors.EVENT_READ | selectors.EVENT_WRITE, lambda: self.receive_and_execute(connection))

    def timeout_handler(self):  
        """
        checks if the timeout has been exceeded
        """
        if time.time() > self.end_time: 
            raise exceptions.TimeoutError

    def run_command(self, connection, command_data: dict):
        """
        process and run command based on received kwargs
        """
        command_data['connection'] = connection
        command_group = command_data['command_group']
        if command_group in self.command_group_map:
            command_group = self.command_group_map[command_group]
            return command_group(**command_data)
        elif command_group in self.command_map:
            command = self.command_map[command_group]
            print(command_data)
            command_data = self.filter_kwargs(command, command_data)
            print(command_data)
            if command_data:
                return command(**command_data)
            return command()
        else:
            raise exceptions.CommandNotFoundError(command_group)
        
    def close_connection(self, connection):
        self.selector.unregister(connection)
        self.connections_list.remove(connection)
        connection.close()

    def broadcast(self, message):
        for connection in self.connections_list:
            self.json_send_explicit(connection, message.dict())

    def receive_and_execute(self, connection):
        """
        receive and process commands
        """
        while True: 
            try:
                message = self.schema_unpack_explicit(connection=connection)  
                self.timeout_handler()  
                kwargs, exit_status = message.kwargs, message.exit_status
                result = self.run_command(connection, kwargs)
                response = schemas.ResponseData(response_message = result)
                self.end_time = time.time() + 300 
                self.json_send_explicit(connection, response.dict()) 
                self.logger.info(message.schema_type)
                if exit_status == 1:
                    self.__exit()
            except (exceptions.TimeoutError, exceptions.Shutdown) as e:
                error_response = schemas.ResponseData(response_message = str(e), exit_status=1)
                self.broadcast(error_response)
                self.logger.warning(str(e))
                for connection in self.connections_list:
                    self.close_connection(connection)
                sys.exit(0)
            except exceptions.Exit as e:
                self.logger.info("user exit initiated")
                error_response = schemas.ResponseData(response_message = str(e), exit_status=1)
                self.json_send_explicit(connection, error_response.dict())
                self.close_connection(connection)
                return
                #self.accept()  # wait for CLI to reconnect
            except OSError:
                self.logger.info("connection was lost, waiting to reconnect")
                self.close_connection(connection)
            except (exceptions.CommandNotFoundError, exceptions.NoConfirmationError, exceptions.InvalidCredentialsReceived, Exception) as e:
                error_str = traceback.format_exc()
                error_response = schemas.ResponseData(response_message = f"{str(e)}")
                self.json_send_explicit(connection, error_response.dict())
                self.logger.warning(f"{error_str}")
    
    def main(self):
        self.selector.register(self.sock, selectors.EVENT_READ | selectors.EVENT_WRITE, self.accept)
        while True:
            try:
                events = self.selector.select()
                for key, mask in events:
                    callback = key.data
                    callback()
            except Exception as e:
                error_str = traceback.format_exc()
                self.logger.warning(error_str)


if __name__ == '__main__':
    server = Server(socket.gethostbyname(socket.gethostname()), 30000)
    server.main()
