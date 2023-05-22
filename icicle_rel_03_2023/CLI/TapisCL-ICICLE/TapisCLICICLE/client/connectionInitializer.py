import client.handlers
import socket
import argparse
from argparse import SUPPRESS
import sys
import pyfiglet
from getpass import getpass
import os
import time
try:
    from ..utilities import schemas
    from ..utilities import socketOpts as SO
    from ..utilities import killableThread
    from ..utilities import decorators
    from ..utilities import args
    from ..utilities import logger
    from . import formatters
    from . import handlers
    from . import parsers
except:
    import utilities.schemas as schemas
    import utilities.socketOpts as SO
    import utilities.killableThread as killableThread
    import utilities.decorators as decorators
    import utilities.args as args
    import utilities.logger as logger
    import client.formatters as formatters
    import client.handlers as handlers
    import client.parsers as parsers


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
server_path = os.path.join(__location__, 'server.py')


class ConnectionInitilializer(handlers.Handlers):
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
                        auth_data = self.auth_handler(auth_request)
                        break
                    except KeyboardInterrupt:
                        pass
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