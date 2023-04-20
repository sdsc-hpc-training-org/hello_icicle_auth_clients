#!/usr/bin/python3
import socket
import argparse
from argparse import SUPPRESS
import sys
import pyfiglet
from getpass import getpass
import os
import time
from pprint import pprint
import json

try:
    from . import schemas
    from . import socketOpts as SO
    from . import helpers
    from . import decorators
    from . import args
except:
    import schemas
    import socketOpts as SO
    import helpers
    import decorators
    import args


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
server_path = os.path.join(__location__, 'server.py')


class CLI(SO.SocketOpts, helpers.OperationsHelper, decorators.DecoratorSetup, helpers.Formatters):
    """
    Receive user input, either direct from bash environment or from the custom interface, then parse these commands and send them to the server to be executed. 
    """
    def __init__(self, IP: str, PORT: int):
        self.ip, self.port = IP, PORT
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        # sets up connection with the server
        self.username, self.url = self.connect()

        # set up argparse
        self.parser = argparse.ArgumentParser(description="Command Line Argument Parser", exit_on_error=False, usage=SUPPRESS)
        self.parser.add_argument('command_group')

        for parameters in args.Args.argparser_args.values():
            self.parser.add_argument(*parameters["args"], **parameters["kwargs"])

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
        connection_info: schemas.StartupData = self.schema_unpack() # receive info from the server whether it is a first time connection
        if connection_info.initial: # if the server is receiving its first connection for the session\
            while True:
                try:
                    url = str(input("\nEnter the link for the tapis service you are connecting to: ")).strip()
                except KeyboardInterrupt:
                    url = " "
                    pass
                url_data = schemas.StartupData(url=url)
                self.json_send(url_data.dict())
                auth_request: schemas.AuthRequest = self.schema_unpack()
                try:
                    username = str(input("\nUsername: ")).strip()
                    password = getpass("Password: ").strip() 
                except KeyboardInterrupt:
                    username, password = " ", " "
                    pass
                auth_data = schemas.AuthData(username = username, password = password)
                self.json_send(auth_data.dict())

                verification: schemas.ResponseData | schemas.StartupData = self.schema_unpack() 
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

    def command_operator(self, kwargs: dict | list, exit_: int=0): 
        """
        parse arguments, handling bash and CLI input
        """
        if isinstance(kwargs, list): # check if the command input is from the CLI, or direct input
            kwargs = vars(self.parser.parse_args(kwargs)) 
        if not kwargs['command_group']:
            return False
        command = schemas.CommandData(kwargs = kwargs, exit_status = exit_)
        return command
    
    def special_forms_ops(self):
        """
        handle special form requests sent by the server
        """
        while True:
            response = self.schema_unpack()
            if response.schema_type == 'FormRequest' and not response.arguments_list:
                form = self.expression_input()
                filled_form = schemas.FormResponse(arguments_list=form)
            elif response.schema_type == 'FormRequest':
                form = self.fillout_form(response.arguments_list)
                filled_form = schemas.FormResponse(arguments_list=form)
            elif response.schema_type == 'AuthRequest':
                if response.secure_input or not response.requires_username:
                    username = self.username
                    password = getpass("Password: ")
                else: 
                    username = input("Username: ")
                    password = getpass("Password: ")
                filled_form = schemas.AuthData(username=username, password=password)
            elif response.schema_type == "ConfirmationRequest":
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
            else:
                return response
            self.json_send(filled_form.dict())

    def print_response(self, response_message):
        """
        format response messages from the server
        """
        if type(response_message) == dict:
            self.recursive_dict_print(response_message)
        elif (type(response_message) == list or 
             type(response_message) == tuple or 
             type(response_message) == set):
            for value in response_message:
                print(value)
        else:
            print(response_message)

    def main(self):
        if len(sys.argv) > 1: # checks if any command line arguments were provided. Does not open CLI
            try:
                kwargs = self.parser.parse_args()
            except:
                print("Invalid Arguments")
                os._exit(0)
            kwargs = vars(kwargs)
            command = self.command_operator(kwargs, exit_=1) # operate with args, send them over
            self.json_send(command.dict())
            response = self.special_forms_ops()
            if response.schema_type == 'ResponseData':
                self.print_response(response.response_message)
            os._exit(0)

        title = pyfiglet.figlet_format("-----------\nTapisCLICICLE\n-----------", font="slant") # print the title when CLI is accessed
        print(title)
        
        while True: # open the CLI if no arguments provided on startup
            try:
                time.sleep(0.01)
                kwargs = self.process_command(str(input(f"[{self.username}@{self.url}] "))) # ask for and process user input
                try:
                    command = self.command_operator(kwargs) # run operations
                except:
                    continue
                if not command:
                    continue
                self.json_send(command.dict())
                response = self.special_forms_ops()
                if response.schema_type == 'ResponseData' and response.exit_status: # if the command was a shutdown or exit, close the program
                    self.print_response(response.response_message)
                    os._exit(0)
                elif response.schema_type == 'ResponseData':
                    self.print_response(response.response_message)
            except KeyboardInterrupt:
                pass # keyboard interrupts mess with the server, dont do it! it wont work anyway, hahahaha
            except WindowsError: # if connection error with the server (there wont be any connection errors)
                print("[-] Connection was dropped. Exiting")
                os._exit(0)
            except Exception as e: # if something else happens
                print(e)


if __name__ == "__main__":
    client = CLI(socket.gethostbyname(socket.gethostname()), 30000)
    client.main()