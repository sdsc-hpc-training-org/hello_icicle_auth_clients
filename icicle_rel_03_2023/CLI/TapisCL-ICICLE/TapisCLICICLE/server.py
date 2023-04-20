import sys
from getpass import getpass
import time
import re
from tapipy.tapis import Tapis
import socket
import os
import logging
from tapisObjectWrappers import Files, Apps, Pods, Systems, Neo4jCLI, PostgresCLI
import typing

try:
    from . import exceptions
    from . import socketOpts as SO
    from . import helpers
    from . import schemas
    from . import decorators
    from . import args
except:
    import exceptions
    import socketOpts as SO
    import helpers
    import schemas
    import decorators
    import args

class Server(SO.SocketOpts, helpers.OperationsHelper, decorators.DecoratorSetup, helpers.DynamicHelpUtility):
    """
    Receives commands from the client and executes Tapis operations
    """
    def __init__(self, IP: str, PORT: int):
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
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        self.connection = None  # initialize the connection variable
        self.end_time = time.time() + 300  # start the countdown on the timeout

        self.logger.info("Awaiting connection")

        self.pods = None
        self.systems = None
        self.files = None
        self.apps = None
        self.neo4j = None
        self.t = None
        self.url = None
        self.access_token = None
        self.username = None
        self.password = None

        self.accept(initial=True)  # connection returns the tapis object and user info

        # instantiate the subsystems
        self.logger.info('initialization complete')
        self.command_group_map = {
            'pods':self.pods,
            'systems':self.systems,
            'files':self.files,
            'apps':self.apps,
        }
        self.command_map = {
            'help':self.help,
            'whoami':self.pods.whoami,
            'exit':self.__exit,
            'shutdown':self.__shutdown,
            'neo4j':self.neo4j,
            'postgres':self.postgres,
            'switch_service':self.tapis_init
        }
        help0, help1 = self.help_generation()
        self.help = dict(help0, **help1)

    @decorators.Auth
    def tapis_init(self, username: str, password: str, link: str) -> tuple[typing.Any, str, str] | None:  # link is the baseURL
        """
        @help: switch the connected tapis service
        """
        start = time.time()
        self.username = username
        self.password = password
        try:
            t = Tapis(base_url=link,
                    username=username,
                    password=password)
            t.get_tokens()
        except:
            raise exceptions.InvalidCredentialsReceived(function=self.tapis_init, cred_type="Tapis Auth")

        self.configure_decorators()
        # V3 Headers
        header_dat = {"X-Tapis-token": t.access_token.access_token,
                      "Content-Type": "application/json"}

        # Service URL
        url = f"{link}/v3"

        # create authenticator for tapis systems
        authenticator = t.access_token
        # extract the access token from the authenticator
        access_token = re.findall(
            r'(?<=access_token: )(.*)', str(authenticator))[0]
        
        if 'win' in sys.platform:
            os.system(f"set JWT={access_token}")
        else: # unix based
            os.system(f"export JWT={access_token}")

        self.pods = Pods(t, username, password, connection=self.connection)
        self.systems = Systems(t, username, password, connection=self.connection)
        self.files = Files(t, username, password, connection=self.connection)
        self.apps = Apps(t, username, password, connection=self.connection)
        self.neo4j = Neo4jCLI(t, username, password, connection=self.connection)
        self.postgres = PostgresCLI(t, username, password, connection=self.connection)

        self.t = t
        self.url = url
        self.access_token = access_token

        self.logger.info(f"initiated in {time.time()-start}")

        return f"Successfully initialized tapis service on {self.url}"

    def accept(self, initial: bool=False):
        """
        accept connection request and initialize communication with the client
        """  
        self.connection, ip_port = self.sock.accept() 
        self.logger.info("Received connection request")

        if initial:  # if this is the first time in the session that the cli is connecting
            startup_data = schemas.StartupData(initial = initial)
            self.json_send(startup_data.dict())
            self.logger.info("send the initial status update")

            for attempt in range(1, 4):
                url: schemas.StartupData = self.schema_unpack().url
                try:
                    auth_request = schemas.AuthRequest()
                    self.json_send(auth_request.dict())
                    auth_data: schemas.AuthData = self.schema_unpack()
                    username, password = auth_data.username, auth_data.password
                    self.tapis_init(link=url, username=username, password=password)
                    self.logger.info("Verification success")
                    break
                except Exception as e:
                    login_failure_data = schemas.ResponseData(response_message = (str(e), attempt))
                    self.json_send(login_failure_data.dict())
                    self.logger.warning(f"Verification failure, {e}")
                    if attempt == 3:  
                        self.logger.error(
                            "Attempted verification too many times. Exiting")
                        os._exit(0)  
                    continue
        else:
            self.configure_decorators()
        startup_result = schemas.StartupData(initial = initial, username = self.username, url = self.url)
        self.logger.info("Connection success")
        self.json_send(startup_result.dict())
        self.logger.info("Final connection data sent")

    def __exit(self):
        """
        @help: exit the CLI without shutting down the service
        """
        raise exceptions.Exit
    
    def __shutdown(self):
        """
        @help: exit the CLI and shutdown the service
        """
        self.logger.info("Shutdown initiated")
        raise exceptions.Shutdown

    def timeout_handler(self):  
        """
        checks if the timeout has been exceeded
        """
        if time.time() > self.end_time: 
            raise exceptions.TimeoutError

    def help(self, command: str):
        """
        @help: returns help information. To get specific help information for tapis services, you can run <service> -c help. enter -c args to see detailed command usage
        """
        if command == "args":
            return args.Args.argparser_args
        elif command in self.help:
            return self.help[command]
        return self.help

    def run_command(self, command_data: dict):
        """
        process and run command based on received kwargs
        """
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
        """
        receive and process commands
        """
        while True: 
            try:
                message = self.schema_unpack()  
                self.timeout_handler()  
                kwargs, exit_status = message.kwargs, message.exit_status
                result = self.run_command(kwargs)
                response = schemas.ResponseData(response_message = result)
                self.end_time = time.time() + 300 
                self.json_send(response.dict()) 
                self.logger.info(message)
                if exit_status == 1:
                    self.__exit()
            except (exceptions.TimeoutError, exceptions.Shutdown) as e:
                error_response = schemas.ResponseData(response_message = str(e), exit_status=1)
                self.json_send(error_response.dict())
                self.logger.warning(str(e))
                sys.exit(0)
            except exceptions.Exit as e:
                self.logger.info("user exit initiated")
                error_response = schemas.ResponseData(response_message = str(e), exit_status=1)
                self.json_send(error_response.dict())
                self.connection.close()  # close the connection
                self.accept()  # wait for CLI to reconnect
            except (exceptions.CommandNotFoundError, exceptions.NoConfirmationError, exceptions.InvalidCredentialsReceived, Exception) as e:
                error_response = schemas.ResponseData(response_message = str(e))
                self.json_send(error_response.dict())
                self.logger.warning(f"{str(e)}\n{e.__traceback__}")



if __name__ == '__main__':
    server = Server(socket.gethostbyname(socket.gethostname()), 30000)
    server.main()
