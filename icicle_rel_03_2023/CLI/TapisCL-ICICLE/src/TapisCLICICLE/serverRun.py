from server import server
import asyncio
import socket


server_obj = server.Server('127.0.0.1', 30000)
asyncio.run(server_obj.main())