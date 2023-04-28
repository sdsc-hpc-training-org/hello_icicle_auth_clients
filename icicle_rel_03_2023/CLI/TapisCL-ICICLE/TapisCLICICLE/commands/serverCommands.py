import sys
import time
import re
from tapipy.tapis import Tapis
import os
import typing

try:
    from ..utilities import exceptions
    from ..utilities import decorators
    from ..utilities import args
except:
    import utilities.exceptions as exceptions
    import utilities.decorators as decorators
    import utilities.args as args


class ServerCommands(decorators.DecoratorSetup):    
    def exit(self, connection=None):
        """
        @help: exit the CLI without shutting down the service
        """
        raise exceptions.Exit
    
    def shutdown(self, connection=None):
        """
        @help: exit the CLI and shutdown the service
        """
        self.logger.info("Shutdown initiated")
        raise exceptions.Shutdown
    
    def help(self, command: str, connection=None):
        """
        @help: returns help information. To get specific help information for tapis services, you can run <service> -c help. enter -c args to see detailed command usage
        """
        if command == "args":
            return args.Args.argparser_args
        elif command in self.help:
            return self.help[command]
        return self.help
    
    def whoami(self, verbose: bool, connection=None) -> str:
        """
        @help: returns the username of the current user
        """
        user_info = self.t.authenticator.get_userinfo()
        if verbose:
            return str(user_info)
        return user_info.username