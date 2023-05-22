from argparse import SUPPRESS
from getpass import getpass
import os
try:
    from ..utilities import schemas
except:
    import utilities.schemas as schemas


class Parsers:
    def process_command(self, command: str) -> list[str]: 
        """
        split the command string into a list. Not sure why this was even made
        """
        command = command.strip().split(' ') 
        return command

    def command_input_parser(self, kwargs: dict | list, exit_: int=0): 
        """
        parse arguments, handling bash and CLI input
        """
        if isinstance(kwargs, list): # check if the command input is from the CLI, or direct input
            kwargs = vars(self.parser.parse_args(kwargs)) 
        if not kwargs['command']:
            return False
        command = schemas.CommandData(kwargs = kwargs, exit_status = exit_)
        return command