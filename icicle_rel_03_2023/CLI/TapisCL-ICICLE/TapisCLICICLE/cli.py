#!/usr/bin/python3
import socket
import argparse
from argparse import SUPPRESS
import sys
import pyfiglet
from getpass import getpass
import os
import time
try:
    from .utilities import schemas
    from .utilities import socketOpts as SO
    from .utilities import helpers
    from .utilities import decorators
    from .utilities import args
except:
    import utilities.schemas as schemas
    import utilities.socketOpts as SO
    import utilities.helpers as helpers
    import utilities.decorators as decorators
    import utilities.args as args


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
server_path = os.path.join(__location__, 'server.py')


class CLI(SO.ClientSocketOpts, decorators.DecoratorSetup, helpers.Formatters, args.Args):
    """
    Receive user input, either direct from bash environment or from the custom interface, then parse these commands and send them to the server to be executed. 
    """
    def __init__(self, IP: str, PORT: int):
        super().__init__()

        self.ip, self.port = IP, PORT
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        # sets up connection with the server
        self.username, self.url = self.connect()

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

    def initialize_server(self): 
        """
        detect client operating system. The local server intitialization is different between unix and windows based systems
        """
        if 'win' in sys.platform:
            os.system(f"pythonw {server_path}")
        else: # unix based
            os.system(f"python {server_path} &")

    @decorators.AnimatedLoading
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
                if startup_flag:
                    startup.kill()
                break
            except Exception as e:
                if not startup_flag:
                    startup = helpers.KillableThread(target=self.initialize_server) # run the server setup on a separate thread
                    startup.start() 
                    startup_flag = True # set the flag to true so the thread runs only once
                    continue

    def connect(self):
        """
        connect to the local server
        """
        self.connection_initialization() 
        #self.connection.connect((self.ip, self.port)) # enable me for debugging. Requires manual server start
        connection_info: schemas.StartupData = self.schema_unpack_explicit(self.connection) # receive info from the server whether it is a first time connection
        if connection_info.initial: # if the server is receiving its first connection for the session\
            while True:
                try:
                    url = str(input("\nEnter the uri for the tapis service you are connecting to: ")).strip()
                except KeyboardInterrupt:
                    url = " "
                    pass
                url_data = schemas.StartupData(url=url)
                self.json_send_explicit(self.connection, url_data.dict())
                print("URL send")
                auth_request: schemas.AuthRequest = self.schema_unpack_explicit(self.connection)
                while True:
                    try:
                        username = str(input("\nUsername: ")).strip()
                        password = getpass("Password: ").strip() 
                        break
                    except KeyboardInterrupt:
                        pass
                auth_data = schemas.AuthData(username = username, password = password)
                self.json_send_explicit(self.connection, auth_data.dict())
                print("sent creds")

                verification: schemas.ResponseData | schemas.StartupData = self.schema_unpack_explicit(self.connection)
                print(verification)
                if verification.schema_type == 'StartupData': # verification success, program moves forward
                    return verification.username, verification.url
                else: # verification failed. User has 3 tries, afterwards the program will shut down
                    print(f"[-] verification failure, attempt # {verification.response_message[1]}")
                    if verification.response_message[1] == 3:
                        sys.exit(0)
                    continue

        return connection_info.username, connection_info.url # return the username and url

    def process_command(self, command: str) -> list[str]: 
        """
        split the command string into a list. Not sure why this was even made
        """
        command = command.strip().split(' ') 
        return command

    def expression_input(self) -> str: 
        """
        Input an expression as requested by the server for something like cypher queries
        """
        print("Enter 'exit' to submit") 
        expression = ''
        line = ''
        while line != 'exit': 
            line = str(input("> "))
            if line != 'exit':
                expression += line
        return expression

    def fillout_form(self, form: list) -> dict:
        """
        fill out a form as requested by the server for more complicated functions
        """
        filled_form = dict()
        for field in form:
            value = str(input(f"{field}: ")).strip()
            if not value:
                value = None
            filled_form.update({field:value})
        return filled_form

    def command_input_parser(self, kwargs: dict | list, exit_: int=0): 
        """
        parse arguments, handling bash and CLI input
        """
        if isinstance(kwargs, list): # check if the command input is from the CLI, or direct input
            kwargs = vars(self.parser.parse_args(kwargs)) 
        if not kwargs['command']:
            return False
        command = schemas.CommandData(kwargs = kwargs, exit_status = exit_)
        return command
    
    def form_handler(self, response):
        if not response.arguments_list:
            form = self.expression_input()
            filled_form = schemas.FormResponse(arguments_list=form)
        else: 
            form = self.fillout_form(response.arguments_list)
            filled_form = schemas.FormResponse(arguments_list=form)
        return filled_form

    def auth_handler(self, response):
        if response.secure_input or not response.requires_username:
            username = self.username
            password = getpass("Password: ")
        else: 
            username = input("Username: ")
            password = getpass("Password: ")
        filled_form = schemas.AuthData(username=username, password=password)
        return filled_form
    
    def confirmation_handler(self, response):
        print(response.message)
        while True:
            decision = str(input("(y/n)"))
            if decision == 'y':
                decision = True
                break
            elif decision == 'n':
                decision = False
                break
            else:
                print("Enter valid response")
        filled_form = schemas.ResponseData(response_message=decision)
        return filled_form
    
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

    def environment_cli_response_stream_handler(self, response):
        if response.schema_type == 'ResponseData' and response.exit_status: # if the command was a shutdown or exit, close the program
            self.print_response(response.response_message)
            os._exit(0)
        elif response.schema_type == 'ResponseData':
            if response.active_username:
                self.username = response.active_username
            if response.url:
                self.url = response.url
            self.print_response(response.response_message)

    def terminal_cli(self):
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