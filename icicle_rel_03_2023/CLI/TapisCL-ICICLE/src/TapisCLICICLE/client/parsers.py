if __name__ != "__main__":
    from ..socketopts import schemas


class Parsers:
    def command_input_parser(self, kwargs: dict | list) -> dict: 
        """
        parse arguments, handling bash and CLI input
        """
        if isinstance(kwargs, list): # check if the command input is from the CLI, or direct input
            kwargs = vars(kwargs.split(' ')) 
        if not kwargs['command']:
            return False
        return kwargs