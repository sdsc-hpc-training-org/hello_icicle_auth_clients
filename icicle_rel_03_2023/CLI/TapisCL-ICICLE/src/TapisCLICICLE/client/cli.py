#!/usr/bin/python3
import socket
import argparse
import sys
import os
import time
import traceback
import subprocess

import pyfiglet
from blessed import Terminal

if __name__ != "__main__":
    from . import handlers
    from ..socketopts import socketOpts, schemas
    from ..commands import decorators
    from ..utilities import killableThread


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(f"{__file__}")))
server_path = os.path.join(__location__, r'../serverRun.py')

ENTRANCE_MESSAGE = \
"""
Welcome to TapisCLICICLE
The server takes a bit of time to start. Please Wait.
If you have VPN enabled and startup fails, disable your VPN
If issues persist, try restarting your computer.
If you find any issues, please create a new issue here: https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/issues
"""
    

class ClientSideConnection(socketOpts.ClientSocketOpts, handlers.Handlers):
    def __init__(self, connection, debug=False):
        super().__init__("client", debug=debug)
        self.connection = connection
    
    def close(self):
        self.connection.close()


class CLI(handlers.Handlers):
    debug=False
    """
    Receive user input, either direct from bash environment or from the custom interface, then parse these commands and send them to the server to be executed. 
    """
    def __init__(self, IP: str, PORT: int):
        super().__init__()

        self.term = Terminal()
        print(f"{self.term.color_rgb(0, 0, 255)}{ENTRANCE_MESSAGE}{self.term.normal}")
        self.ip, self.port = IP, PORT
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        # set up argparse
        self.parser = None

        setup_message = schemas.ResponseData(request_content={'setup_success':True})
        try:
            self.username, self.url = self.connect()
            self.connection.send(setup_message)
        except ConnectionAbortedError:
            print("Server timed out during authentication. Try again")
            sys.exit(0)
        except (KeyboardInterrupt, Exception) as e:
            error_str = traceback.format_exc()
            if self.debug:
                print(error_str)
            print(e)
            setup_message.error = str(e)
            setup_message.request_content['setup_success'] = False
            self.connection.send(setup_message)
            sys.exit(0)

        self.pwd = ""
        self.current_system = ""

    def parser_error(self, args):
        print(f"Ignoring unrecognized arguments: {args}")
    
    def configure_parser(self, arguments):
        parser = argparse.ArgumentParser(description="Command Line Argument Parser", exit_on_error=False, usage=argparse.SUPPRESS, add_help=False, conflict_handler='resolve')
        parser.add_argument('command_selection')
        parser.add_argument('positionals', nargs='*')
        parser.error = self.parser_error

        for arg in arguments.values():
            print(arg['truncated_arg'])
        for arg_name, arg in arguments.items():
            parser.add_argument(f"-{arg['truncated_arg']}", arg['full_arg'],
                                action=arg['action'])
        return parser

    def initialize_server(self): 
        """
        detect client operating system. The local server intitialization is different between unix and windows based systems
        """
        if 'win' in sys.platform:
            os.system(rf"pythonw {server_path}")
        else: # unix based
            subprocess.Popen(['nohup', 'python3', server_path, '&'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #@decorators.AnimatedLoading
    def connection_initialization(self):
        """
        start the local server through the client
        """
        startup_flag = False
        timeout_time = time.time() + 30 # server setup timeout. If expires, there is a problem!
        while True:
            if time.time() > timeout_time: # connection timeout condition
                sys.stdout.write("\r[-] Connection timeout")
                sys.exit(0)
            try:
                self.connection.connect((self.ip, self.port)) 
                self.connection = ClientSideConnection(self.connection, debug=self.debug)
                if startup_flag:
                    startup.kill()
                break
            except Exception as e:
                if not startup_flag:
                    startup = killableThread.KillableThread(target=self.initialize_server, daemon=True) # run the server setup on a separate thread
                    startup.start() 
                    startup_flag = True # set the flag to true so the thread runs only once
                    continue

    def auth(self):
        while True:
            server_auth_request: schemas.AuthRequest = self.connection.receive()
            if not server_auth_request.message and not server_auth_request.request_content:
                self.print_response(server_auth_request.error)
                sys.exit(0)
            elif server_auth_request.auth_request_type == "success":
                self.print_response(server_auth_request.message)
                return server_auth_request.message['username'], server_auth_request.message['url']
            form_response = self.universal_message_handler(server_auth_request, self.term)
            if not form_response:
                break
            client_response_request = schemas.AuthRequest(auth_request_type=server_auth_request.auth_request_type, request_content=form_response)
            self.connection.send(client_response_request)
        
    def connect(self):
        """
        connect to the local server
        """
        self.connection_initialization() 
        #self.connection.connect((self.ip, self.port)) # enable me for debugging. Requires manual server start
        connection_info: schemas.StartupData = self.connection.receive() # receive info from the server whether it is a first time connection
        if connection_info.initial: # if the server is receiving its first connection for the session\
            username, url = self.auth()
        else:
            username, url = connection_info.username, connection_info.url
        arguments: schemas.ResponseData = self.connection.receive()
        self.parser = self.configure_parser(arguments.request_content)

        return username, url # return the username and url

    def interface(self, kwargs):
        if not kwargs['command_selection']:
            return
        command_request = schemas.CommandData(request_content=kwargs)
        self.connection.send(command_request)
        while True:
            command_response = self.connection.receive()
            if isinstance(command_response, schemas.ResponseData):
                self.url, self.username = command_response.url, command_response.active_username
                self.pwd, self.current_system = command_response.pwd, command_response.system
                if command_response.exit_status:
                    print("Exit initiated")
                    sys.exit(0)
            handled_response = self.universal_message_handler(command_response, self.term)
            if not handled_response:
                break
            handled_response = schemas.FormResponse(request_content=handled_response)
            self.connection.send(handled_response)

    def terminal_cli(self):
        try:
            kwargs = self.parser.parse_args()
        except:
            print("Invalid Arguments")
            sys.exit(0)
        kwargs = vars(kwargs)
        self.interface(kwargs)
        sys.exit(0)

    def cli_window(self):
        title = pyfiglet.figlet_format("-----------\nTapisCLICICLE\n-----------", font="slant") # print the title when CLI is accessed
        print(title)
        print(r"""Enter 'exit' to exit the client
                Enter 'shutdown' to shut down the client and server
                Enter 'Help' to show command options""")
        while True:
            try:
                time.sleep(0.01)
                kwargs: dict = vars(self.parser.parse_args(str(input(f"[{self.username}@{self.url}][{self.current_system}]{self.pwd} ")).split(" ")))
                self.interface(kwargs)
            except KeyboardInterrupt:
                continue
            except (ConnectionAbortedError, ConnectionResetError):
                print("Server shutdown, exiting")
                sys.exit(0)
            except (TypeError, argparse.ArgumentError, argparse.ArgumentTypeError) as e:
                print(e)
                error_str = traceback.format_exc()
                print(error_str)
                print("Invalid command")
            except Exception as e:
                error_str = traceback.format_exc()
                if self.debug:
                    print(error_str)
                print(e)
                error_message = schemas.ResponseData(error=str(e))
                self.connection.send(error_message)
        

    def main(self):
        if len(sys.argv) > 1: # checks if any command line arguments were provided. Does not open CLI
            self.terminal_cli()
        self.cli_window()


if __name__ == "__main__":
    client = CLI(socket.gethostbyname(socket.gethostname()), 30000)
    client.main()