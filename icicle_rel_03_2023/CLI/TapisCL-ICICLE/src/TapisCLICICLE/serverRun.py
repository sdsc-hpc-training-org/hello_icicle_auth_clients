from server import server
import asyncio
import socket


if __name__ == "__main__":
    #try:
    server_obj = server.Server('127.0.0.1', 30000)
    asyncio.run(server_obj.main())
    # except KeyboardInterrupt:
    #     if server_obj:
    #         server_obj.running = False
