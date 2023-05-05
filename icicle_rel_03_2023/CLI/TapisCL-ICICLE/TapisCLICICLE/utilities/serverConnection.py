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

    def close(self):
        self.reader.close()
        self.writer.close()