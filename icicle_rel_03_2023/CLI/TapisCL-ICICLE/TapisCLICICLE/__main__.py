import socket
import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
import TapisCLICICLE.client.cli as cli


def client_start():
    client_object = cli.CLI(socket.gethostbyname(socket.gethostname()), 30000)
    client_object.main()

client_start()