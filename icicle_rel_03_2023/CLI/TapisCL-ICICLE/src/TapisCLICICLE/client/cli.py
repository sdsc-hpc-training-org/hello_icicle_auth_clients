#!/usr/bin/python3
import socket
import argparse
import sys
import os
import time

import pyfiglet

if __name__ != "__main__":
    from . import formatters, parsers, handlers
    from ..socketopts import socketOpts, schemas
    from ..commands import decorators, args
    from ..utilities import killableThread
    from ..server import auth


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(f"{__file__}")))
server_path = os.path.join(__location__, r'..\serverRun.py')


class ClientSideConnection(socketOpts.ClientSocketOpts, handlers.Handlers):
    def __init__(self, connection):
        self.connection = connection

    # def receive(self):
    #     """
    #     receives and returns data sent by the server. If the server is requesting a form
    #     """
    #     data = self.recv()
    #     if data.schema_type in ("FormRequest", "AuthRequest"):
    #         self.send(self.form_handler(data.request_content))
    #         return self.receive()
    #     elif data.schema_type == "ConfirmationRequest":
    #         self.send(self.confirmation_handler())
    #         return self.receive()
    #     return data
    
    def close(self):
        self.connection.close()


class CLI(auth.AuthClientSide, socketOpts.ClientSocketOpts, decorators.DecoratorSetup, formatters.Formatters, args.Args, parsers.Parsers, handlers.Handlers):
    """
    Receive user input, either direct from bash environment or from the custom interface, then parse these commands and send them to the server to be executed. 
    """
    def __init__(self, IP: str, PORT: int):
        super().__init__()

        self.ip, self.port = IP, PORT
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        # sets up connection with the server
        self.username = None
        self.password = None

        # set up argparse
        self.parser = argparse.ArgumentParser(description="Command Line Argument Parser", exit_on_error=False, usage=argparse.SUPPRESS, conflict_handler='resolve')
        self.parser.add_argument('command')

        self.message_handlers = {
            'FormRequest':self.form_handler,
            'AuthRequest':self.auth_handler,
            'ConfirmationRequest':self.confirmation_handler,
        }

        for parameters in self.argparser_args.values():
            self.parser.add_argument(*parameters["args"], **parameters["kwargs"])

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
                self.connection = ClientSideConnection(self.connection)
                if startup_flag:
                    startup.kill()
                break
            except Exception as e:
                if not startup_flag:
                    startup = killableThread.KillableThread(target=self.initialize_server) # run the server setup on a separate thread
                    startup.start() 
                    startup_flag = True # set the flag to true so the thread runs only once
                    continue

    def connect(self):
        """
        connect to the local server
        """
        self.connection_initialization() 
        #self.connection.connect((self.ip, self.port)) # enable me for debugging. Requires manual server start
        connection_info: schemas.StartupData = self.connection.receive() # receive info from the server whether it is a first time connection
        if connection_info.initial: # if the server is receiving its first connection for the session\
            self.auth()
        return connection_info.username, connection_info.url # return the username and url
    
    def special_forms_ops(self):
        """
        handle special form requests sent by the server
        """
        while True:
            message = self.connection.receive()
            message_type = message.schema_type
            if message_type in self.message_handlers.keys():
                filled_form = self.message_handlers[message_type](message)
            else:
                return message
            self.connection.send(filled_form)

    def terminal_cli(self):
        self.username, self.url = self.connect()
        try:
            kwargs = self.parser.parse_args()
        except:
            print("Invalid Arguments")
            os._exit(0)
        kwargs = vars(kwargs)
        command = self.command_input_parser(kwargs, exit_=1) # operate with args, send them over
        self.connection.send(command)
        response = self.special_forms_ops()
        if response.schema_type == 'ResponseData':
            self.print_response(response.response_message)
        os._exit(0)

    def environment_cli(self):
        self.username, self.url = self.connect()
        title = pyfiglet.figlet_format("-----------\nTapisCLICICLE\n-----------", font="slant") # print the title when CLI is accessed
        print(title)
        print(r"""If you find any issues, please create a new issue here: https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/issues
                Enter 'exit' to exit the client
                Enter 'shutdown' to shut down the client and server
                Enter 'Help' to show command options""")
        
        while True: # open the CLI if no arguments provided on startup
            try:
                time.sleep(0.01)
                kwargs = self.process_command(str(input(f"[{self.username}@{self.url}] "))) # ask for and process user input
                try:
                    command = self.command_input_parser(kwargs) # run operations
                except:
                    continue
                if not command:
                    continue
                self.connection.send(command)
                response = self.special_forms_ops()
                self.environment_cli_response_stream_handler(response)
            except KeyboardInterrupt:
                pass # keyboard interrupts mess with the server, dont do it! it wont work anyway, hahahaha
            except WindowsError: # if connection error with the server (there wont be any connection errors)
                print("[-] Connection was dropped. Exiting")
                os._exit(0)
            except Exception as e: # if something else happens
                print(e)

    def main(self):
        if len(sys.argv) > 1: # checks if any command line arguments were provided. Does not open CLI
            self.terminal_cli()
        self.environment_cli()


if __name__ == "__main__":
    client = CLI(socket.gethostbyname(socket.gethostname()), 30000)
    client.main()