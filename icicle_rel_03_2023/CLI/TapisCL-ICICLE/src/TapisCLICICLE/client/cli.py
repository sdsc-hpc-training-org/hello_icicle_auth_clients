#!/usr/bin/python3
import socket
import argparse
import sys
import os
import time

import pyfiglet

if __name__ != "__main__":
    from . import parsers, handlers
    from ..socketopts import socketOpts, schemas
    from ..commands import decorators, args
    from ..utilities import killableThread


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(f"{__file__}")))
server_path = os.path.join(__location__, r'..\serverRun.py')
    

class ClientSideConnection(socketOpts.ClientSocketOpts, handlers.Handlers):
    def __init__(self, connection, debug=False):
        super().__init__(__name__, debug=debug)
        self.connection = connection
    
    def close(self):
        self.connection.close()


class CLI(socketOpts.ClientSocketOpts, decorators.DecoratorSetup, args.Args, parsers.Parsers, handlers.Handlers):
    """
    Receive user input, either direct from bash environment or from the custom interface, then parse these commands and send them to the server to be executed. 
    """
    def __init__(self, IP: str, PORT: int):
        super().__init__()

        self.ip, self.port = IP, PORT
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        # set up argparse
        self.parser = argparse.ArgumentParser(description="Command Line Argument Parser", exit_on_error=False, usage=argparse.SUPPRESS, conflict_handler='resolve')
        self.parser.add_argument('command')

        for parameters in self.argparser_args.values():
            self.parser.add_argument(*parameters["args"], **parameters["kwargs"])

        self.username, self.password = self.connect()

    def initialize_server(self): 
        """
        detect client operating system. The local server intitialization is different between unix and windows based systems
        """
        if 'win' in sys.platform:
            os.system(rf"pythonw {server_path}")
        else: # unix based
            os.system(f"python {server_path} &")

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
                os._exit(0)
            try:
                self.connection.connect((self.ip, self.port)) 
                self.connection = ClientSideConnection(self.connection, debug=True)
                if startup_flag:
                    startup.kill()
                break
            except Exception as e:
                if not startup_flag:
                    startup = killableThread.KillableThread(target=self.initialize_server) # run the server setup on a separate thread
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
                return server_auth_request.message['username'], server_auth_request.message['password']
            form_response = self.universal_message_handler(server_auth_request)
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
        return username, url # return the username and url

    def interface(self, kwargs):
        if not kwargs['command']:
            return
        command_request = schemas.CommandData(request_content=kwargs)
        self.connection.send(command_request)
        while True:
            command_response = self.connection.receive()
            handled_response = self.universal_message_handler(command_response)
            if not handled_response:
                break
            self.connection.send(handled_response)

    def terminal_cli(self):
        try:
            kwargs = self.parser.parse_args()
        except:
            print("Invalid Arguments")
            os._exit(0)
        kwargs = vars(kwargs)
        self.interface(kwargs)
        os._exit(0)

    def cli_window(self):
        title = pyfiglet.figlet_format("-----------\nTapisCLICICLE\n-----------", font="slant") # print the title when CLI is accessed
        print(title)
        print(r"""If you find any issues, please create a new issue here: https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/issues
                Enter 'exit' to exit the client
                Enter 'shutdown' to shut down the client and server
                Enter 'Help' to show command options""")
        while True:
            try:
                time.sleep(0.01)
                kwargs: dict = str(input(f"[{self.username}@{self.url}] ")).split(' ')
                self.interface(kwargs)
            except KeyboardInterrupt:
                continue

    def main(self):
        if len(sys.argv) > 1: # checks if any command line arguments were provided. Does not open CLI
            self.terminal_cli()
        self.cli_window()


if __name__ == "__main__":
    client = CLI(socket.gethostbyname(socket.gethostname()), 30000)
    client.main()