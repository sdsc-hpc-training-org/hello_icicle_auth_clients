import socket
import asyncio
from TapisCLICICLE.client.cli import CLI


def client_start():
    client_object = CLI('127.0.0.1', 30000)
    client_object.main()


if __name__ == "__main__":
    client_start()

# server = Server(socket.gethostbyname(socket.gethostname()), 30000)
# asyncio.run(server.main())