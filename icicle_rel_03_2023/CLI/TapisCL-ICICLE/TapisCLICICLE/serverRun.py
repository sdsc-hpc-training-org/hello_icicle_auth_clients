import socket
from server.server import Server
import asyncio

server = Server(socket.gethostbyname(socket.gethostname()), 30000)
asyncio.run(server.main())