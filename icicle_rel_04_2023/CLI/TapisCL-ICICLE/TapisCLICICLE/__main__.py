from TapisCLICICLE.cli import CLI
import socket


client = CLI(socket.gethostbyname(socket.gethostname()), 30000)
client.main()