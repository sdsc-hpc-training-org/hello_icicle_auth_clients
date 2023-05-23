#!/usr/bin/python3
import socket
import argparse
from argparse import SUPPRESS
import sys
import pyfiglet
from getpass import getpass
import os
import time
project_root = os.path.dirname(os.path.abspath(f"{__file__}\.."))
print(project_root)
sys.path.append(project_root)


import TapisCLICICLE.utilities.schemas as schemas
import TapisCLICICLE.utilities.socketOpts as SO
import TapisCLICICLE.utilities.decorators as decorators
import TapisCLICICLE.utilities.args as args
import formatters
import handlers
import parsers
import connectionInitializer


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
server_path = os.path.join(__location__, r'..\serverRun.py')


class CLI(SO.ClientSocketOpts, decorators.DecoratorSetup, formatters.Formatters, args.Args, parsers.Parsers, connectionInitializer.ConnectionInitilializer):
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
        self.parser = argparse.ArgumentParser(description="Command Line Argument Parser", exit_on_error=False, usage=SUPPRESS, conflict_handler='resolve')
        self.parser.add_argument('command')

        self.message_handlers = {
            'FormRequest':self.form_handler,
            'AuthRequest':self.auth_handler,
            'ConfirmationRequest':self.confirmation_handler,
        }

        for parameters in self.argparser_args.values():
            self.parser.add_argument(*parameters["args"], **parameters["kwargs"])

        print(r"If you find any issues, please create a new issue here: https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/issues")
    
    def special_forms_ops(self):
        """
        handle special form requests sent by the server
        """
        while True:
            message = self.schema_unpack_explicit(self.connection)
            message_type = message.schema_type
            if message_type in self.message_handlers.keys():
                filled_form = self.message_handlers[message_type](message)
            else:
                return message
            self.json_send_explicit(self.connection, filled_form.dict())

    def terminal_cli(self):
        self.username, self.url = self.connect()
        try:
            kwargs = self.parser.parse_args()
        except:
            print("Invalid Arguments")
            os._exit(0)
        kwargs = vars(kwargs)
        command = self.command_input_parser(kwargs, exit_=1) # operate with args, send them over
        self.json_send_explicit(self.connection, command.dict())
        response = self.special_forms_ops()
        if response.schema_type == 'ResponseData':
            self.print_response(response.response_message)
        os._exit(0)

    def environment_cli(self):
        self.username, self.url = self.connect()
        title = pyfiglet.figlet_format("-----------\nTapisCLICICLE\n-----------", font="slant") # print the title when CLI is accessed
        print(title)
        
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
                self.json_send_explicit(self.connection, command.dict())
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