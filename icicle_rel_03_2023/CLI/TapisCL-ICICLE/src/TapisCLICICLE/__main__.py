import socket
import asyncio
from TapisCLICICLE.client.cli import CLI

def client_start():
    client_object = CLI(socket.gethostbyname(socket.gethostname()), 30000)
    client_object.main()


if __name__ == "__main__":
    print("The server takes a bit of time to start. Please Wait")
    client_start()

# server = Server(socket.gethostbyname(socket.gethostname()), 30000)
# asyncio.run(server.main())