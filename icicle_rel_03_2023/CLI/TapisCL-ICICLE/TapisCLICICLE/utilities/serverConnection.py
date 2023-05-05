try:
    from . import socketOpts
except:
    import socketOpts

class ServerConnection(socketOpts.ServerSocketOpts):
    """
    connection object to wrap around async reader and writer to make work easier
    """
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def close(self):
        self.reader.feed_eof()
        await self.reader.wait_eof()
        self.writer.close()
        await self.writer.wait_closed()