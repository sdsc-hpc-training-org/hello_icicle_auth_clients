from TapisCLICICLE.cli import CLI
import socket


def client_start():
    client = CLI(socket.gethostbyname(socket.gethostname()), 30000)
    client.main()

client_start()