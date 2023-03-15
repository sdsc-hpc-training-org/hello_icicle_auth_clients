#!/usr/bin/python3

import socket
import argparse
from argparse import SUPPRESS
import sys
import json
import pyfiglet
from getpass import getpass
import threading
import os
import time
from pprint import pprint


class CLI:
    def __init__(self, IP, PORT):
        self.ip, self.port = IP, PORT
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        # sets up connection with the server
        self.username, self.url = self.connect()

        # set up argparse
        self.parser = argparse.ArgumentParser(description="Command Line Argument Parser", exit_on_error=False, usage=SUPPRESS)
        self.parser.add_argument('command_group')
        self.parser.add_argument('-c', '--command')
        self.parser.add_argument('-i', '--id')
        self.parser.add_argument('-t', '--template')
        self.parser.add_argument('-u', '--username')
        self.parser.add_argument('-L', '--level')
        self.parser.add_argument('-v', '--version')
        self.parser.add_argument('-F', '--file')
        self.parser.add_argument('-n', '--name')
        self.parser.add_argument('--uuid')
        self.parser.add_argument('-d', '--description')
        self.parser.add_argument('-p', '--password')
        self.parser.add_argument('-e', '--expression')
        self.parser.add_argument('-V', '--verbose', action='store_true')

        # special case commands. These require special inputs or operations to complete properly
        self.password_commands = ['set_password'] # need password input
        self.confirmation_commands = ['restart_pod', 'delete_pod', 'delete_app', 'delete_system'] # need confirmation
        self.subclients = ['neo4j'] # need separate CLI

    def json_send(self, data): # package data in json and send
        json_data = json.dumps(data)
        self.connection.send(bytes((json_data), ('utf-8')))

    def json_receive(self): # Receive and unpack json 
        json_data = ""
        while True:
            try: #to handle long files, so that it continues to receive data and create a complete file
                json_data = json_data + self.connection.recv(1024).decode('utf-8') #formulate a full file. Combine sequential data streams to unpack
                return json.loads(json_data) #this is necessary whenever transporting any large amount of data over TCP streams
            except ValueError:
                continue

    def initialize_server(self): # function detects operating system. Runs OS command to start the server
        if 'win' in sys.platform: # windows
            os.system(r"pythonw C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\client-server\server.py")
        else: # unix based
            os.system(r"python C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\client-server\server.py &")

    def connection_initialization(self): # patience. This sometimes takes a while
        startup_flag = False # flag to tell code not to run multiple server setup threads at once
        dot_count = 1 # for pretty initialization visual
        timeout_time = time.time() + 30 # server setup timeout. If expires, there is a problem!
        print("[+] Now connecting. This might take a while...\n")
        animation = ['.  ','.. ', '...']
        while True:
            if time.time() > timeout_time: # connection timeout condition
                sys.stdout.write("\r[-] Connection timeout")
                os._exit(0)
            try:
                self.connection.connect((self.ip, self.port)) # try to establish a connection
                break
            except Exception as e:
                if not startup_flag:
                    startup = threading.Thread(target=self.initialize_server) # run the server setup on a separate thread
                    startup.start() 
                    startup_flag = True # set the flag to true so the thread runs only once
                    continue
                else: # prints out dots, purely visual
                    sys.stdout.write(f'\r[+] Starting Server{animation[dot_count]}')
                    sys.stdout.flush()
                    if dot_count == 2:
                        dot_count = 0
                    else:
                        dot_count += 1
                    continue

    def connect(self):
        #self.connection_initialization() # connect to the server
        self.connection.connect((self.ip, self.port)) # enable me for debugging. Requires manual server start
        connection_info = self.json_receive() # receive info from the server whether it is a first time connection
        if connection_info['connection_type'] == "initial": # if the server is receiving its first connection for the session\
            while True:
                username = str(input("\nUsername: ")) # take the username
                password = getpass("Password: ") # take the password
                self.json_send({"username":username, "password":password}) # send the username and password to the server to be used
                verification = self.json_receive() # server responds saying if the verification succeeded or not
                if verification[0]: # verification success, program moves forward
                    print("[+] verification success")
                    break
                else: # verification failed. User has 3 tries, afterwards the program will shut down
                    print("[-] verification failure")
                    if verification[1] == 3:
                        sys.exit(0)
                    continue

            url = self.json_receive() # receive the url
            return username, url # return the username and url

        elif connection_info['connection_type'] == 'continuing': # if it is not the first connection to the session ( if user exited and is reconnecting )
            username, url = connection_info['username'], connection_info['url'] # receive username and URL
            return username, url # return username and url

    def process_command(self, command): # process CLI application input (when user enters dedicated CLI)
        command = command.split(' ') # split the command into a list for processing
        return command

    def expression_input(self): # for subclients. Pods and apps running through Tapis will have their own inputs. This gives user an interface
        print("Enter 'exit' to submit") # user must enter exit to submit their input
        expression = ''
        while True: # handles multiple lines of input. Good for neo4j expressions
            line = str(input("> "))
            if line == 'exit':
                break
            expression += line
        return expression

    def check_command(self, **kwargs): # runs command checking operations for special functions
        command = kwargs['command']
        if command in self.password_commands: # does the command need password confirmation?
            kwargs['password'] = getpass(f"{command} password: ") # enter password separately and securely
        elif command in self.confirmation_commands: # does the command require some confirmation to execute?
            decision = str(input("Are you sure? y/n\n")) # ask for confirmation separately
            if decision != 'y':
                return False # if yes is not given, false is returned and the function will not be sent to the server, or executed
        elif kwargs['command_group'] in self.subclients and not kwargs['file']: # does the command require additional input?
            kwargs['expression'] = self.expression_input() # provide more user input
            
        return kwargs

    def command_operator(self, kwargs, exit_=False): # parses command input
        if isinstance(kwargs, list): # check if the command input is from the CLI, or direct input
            try:
                kwargs = vars(self.parser.parse_args(kwargs)) # parse the arguments
            except:
                raise Exception("[-] Invalid Arguments")
        if not kwargs['command_group']:
            return False # if there is no command provided, the function returns false, and nothing is executed
        
        kwargs = self.check_command(**kwargs) # check function conditions
        if not kwargs: # if confirmation failed
            raise Exception("[-] Confirmation not given. Command not executed") # raise an error, dont execute anything
        self.json_send({'kwargs':kwargs, 'exit':exit_}) # send the json package with the command, and exit status. If exit is true, the CLI automatically exits on command execution
        
        result = self.json_receive() # received command result from the server
        return result

    def main(self):
        if len(sys.argv) > 1: # checks if any command line arguments were provided. Does not open CLI
            try:
                kwargs = self.parser.parse_args()
                kwargs = vars(kwargs)
                result = self.command_operator(kwargs, exit_=True) # operate with args, send them over
                if isinstance(result, dict): # if get a dict back
                    pprint(result) # pretty print
                else:
                    print(result) # just print if not a dict
            except Exception as e:
                print(e)
            sys.exit(0)

        title = pyfiglet.figlet_format("Tapiconsole", font="slant") # print the title when CLI is accessed
        print(title)
        
        while True: # open the CLI if no arguments provided on startup
            try:
                kwargs = self.process_command(str(input(f"[{self.username}@{self.url}] "))) # ask for and process user input
                result = self.command_operator(kwargs) # run operations
                if not result: # if any problem like bad confirmation or nonexistance happened, try again
                    continue
                if result == '[+] Exiting' or '[+] Shutting down' in result: # if the command was a shutdown or exit, close the program
                    print(result)
                    os._exit(0)
                if isinstance(result, dict): # if the result comes as a dict, pretty print it
                    pprint(result)
                    continue
                print(result) # just print it if its anything else
            except KeyboardInterrupt:
                pass # keyboard interrupts mess with the server, dont do it! it wont work anyway, hahahaha
            except WindowsError: # if connection error with the server (there wont be any connection errors)
                raise ConnectionError("[-] Connection was dropped. Exiting")
            except Exception as e: # if something else happens
                 print(e)


if __name__ == "__main__":
    try:
        client = CLI('127.0.0.1', 3000)
    except Exception as e:
        print(e)
        print('[-] Invalid login, try again')
        sys.exit(1)
    client.main()