import pyfiglet
import argparse
import sys
from getpass import getpass
import time
import re
from tapipy.tapis import Tapis
import tapipy.tapis
import socket
import json
import threading
import multiprocessing
import os
import logging
from tapisObjectWrappers import Files, Apps, Pods, Systems, Neo4jCLI
from TypeEnforcement.type_enforcer import TypeEnforcer
import typing

try:
    from . import exceptions
    from . import SocketOpts as SO
    from . import helpers
    from . import schemas
except:
    import exceptions
    import SocketOpts as SO
    import helpers
    import schemas

class Server(SO.SocketOpts, helpers.OperationsHelper):
    @TypeEnforcer.enforcer(recursive=True)
    def __init__(self, IP: str, PORT: int):
        # logger setup
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler(stream=sys.stdout)

        log_path = r"\logs"
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
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        self.connection = None  # initialize the connection variable
        self.end_time = time.time() + 300  # start the countdown on the timeout

        self.logger.info("Awaiting connection")
        self.username, self.password, self.t, self.url, self.access_token = self.accept(
            initial=True)  # connection returns the tapis object and user info

        # instantiate the subsystems
        self.pods = Pods(self.t, self.username, self.password)
        self.systems = Systems(self.t, self.username, self.password)
        self.files = Files(self.t, self.username, self.password)
        self.apps = Apps(self.t, self.username, self.password)
        self.neo4j = Neo4jCLI(self.t, self.username, self.password)
        self.logger.info('initialization complee')

        self.command_group_map = {
            'pods':self.pods.cli,
            'systems':self.systems.cli,
            'files':self.files.cli,
            'apps':self.apps.cli
        }
        self.command_map = {
            'help':self.help,
            'whoami':self.pods.whoami,
            'exit':self.__exit,
            'shutdown':self.__shutdown
        }

    @TypeEnforcer.enforcer(recursive=True)
    def tapis_init(self, username: str, password: str) -> tuple[typing.Any, str, str] | None:  # initialize the tapis opject
        start = time.time()
        base_url = "https://icicle.tapis.io"
        t = Tapis(base_url=base_url,
                  username=username,
                  password=password)
        t.get_tokens()

        # V3 Headers
        header_dat = {"X-Tapis-token": t.access_token.access_token,
                      "Content-Type": "application/json"}

        # Service URL
        url = f"{base_url}/v3"

        # create authenticator for tapis systems
        authenticator = t.access_token
        # extract the access token from the authenticator
        access_token = re.findall(
            r'(?<=access_token: )(.*)', str(authenticator))[0]

        print(type(t))
        return t, url, access_token

    @TypeEnforcer.enforcer(recursive=True)
    def accept(self, initial: bool=False):  # function to accept CLI connection to the server
        self.connection, ip_port = self.sock.accept()  # connection request is accepted
        self.logger.info("Received connection request")
        startup_data = schemas.StartupData(initial = initial)
        self.json_send(startup_data.dict())
        if initial:  # if this is the first time in the session that the cli is connecting
            # tell the client that it is the first connection
            self.logger.info("Sent initial status update")
            # give the cli 3 attempts to provide authentication
            for attempt in range(1, 4):
                credentials = self.schema_unpack()  # receive the username and password
                self.logger.info("Received credentials")
                username, password = credentials.username, credentials.password
                try:
                    # try intializing tapis with the supplied credentials
                    t, url, access_token = self.tapis_init(username, password)
                    # send to confirm to the CLI that authentication succeeded
                    self.logger.info("Verification success")
                    startup_result = schemas.StartupData(initial = initial, username = username, url = url)
                    break
                except Exception as e:
                    # send failure message to CLI
                    login_failure_data = schemas.ResponseData(response_message = (str(e), attempt))
                    self.json_send(login_failure_data.dict())
                    self.logger.warning("Verification failure")
                    if attempt == 3:  # If there have been 3 login attempts
                        self.logger.error(
                            "Attempted verification too many times. Exiting")
                        os._exit(0)  # shutdown the server
                    continue
        else:
            startup_result = schemas.StartupData(initial = initial, username = self.username, url = self.url)
        self.logger.info("Connection success")
        self.json_send(startup_result.dict())
        self.logger.info("Final connection data sent")
        if initial:
            return username, password, t, url, access_token

    def __exit(self):
        raise exceptions.Exit
    
    def __shutdown(self):
        self.logger.info("Shutdown initiated")
        raise exceptions.Shutdown

    def timeout_handler(self):  # handle timeouts
        if time.time() > self.end_time:  # if the time exceeds the timeout time
            raise exceptions.TimeoutError
    
    def help(self):
        with open(r'help.json', 'r') as f:
            return json.load(f)

    def run_command(self, command_data: dict):  # process and run commands
        command_group = command_data['command_group']
        if command_group in self.command_group_map:
            command_group = self.command_group_map[command_group]
            return command_group(**command_data)
        elif command_group in self.command_map:
            command = self.command_map[command_group]
            command_data = self.filter_kwargs(command, command_data)
            if command_data:
                return command(**command_data)
            return command()
        else:
            raise exceptions.CommandNotFoundError(command_group)

    def main(self):
        while True: 
            try:
                message = self.schema_unpack()  
                self.timeout_handler()  
                kwargs, exit_status = message.kwargs, message.exit_status
                result = self.run_command(kwargs)
                response = schemas.ResponseData(response_message = result)
                self.end_time = time.time() + 300 
                self.json_send(response.dict()) 
                if exit_status == 1:
                    self.__exit()
            except exceptions.CommandNotFoundError as e:
                error_response = schemas.ResponseData(response_message = str(e))
                self.json_send(error_response.dict())
            except (exceptions.TimeoutError, exceptions.Shutdown) as e:
                error_response = schemas.ResponseData(response_message = str(e), exit_status=1)
                self.json_send(error_response.dict())
                sys.exit(0)
            except exceptions.Exit as e:
                self.logger.info("user exit initiated")
                error_response = schemas.ResponseData(response_message = str(e), exit_status=1)
                self.json_send(error_response.dict())
                self.connection.close()  # close the connection
                self.accept()  # wait for CLI to reconnect



if __name__ == '__main__':
    server = Server('127.0.0.1', 3000)
    server.main()
