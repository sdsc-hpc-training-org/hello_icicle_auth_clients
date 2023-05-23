from server import server
import asyncio
import socket


server_obj = server.Server(socket.gethostbyname(socket.gethostname()), 30000)
asyncio.run(server_obj.main())