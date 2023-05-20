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
    from ..utilities import schemas
    from ..utilities import helpers
    from . import baseCommand
except:
    import utilities.helpers as helpers
    import utilities.exceptions as exceptions
    import utilities.decorators as decorators
    import utilities.args as args
    import utilities.decorators as decorators
    import utilities.schemas as schemas
    import commands.baseCommand as baseCommand


class switch_service(baseCommand.BaseCommand):
    """
    @help: switch the connected tapis service
    @todo: upgrade to federated auth
    """
    decorator = decorators.Auth()
    async def run(self, username: str, link: str, *args, **kwargs) -> tuple[typing.Any, str, str] | None:  # link is the baseURL
        return kwargs['server'].switch_session(username, link, *args, **kwargs)
      

class exit(baseCommand.BaseCommand):
    """
    @help: exit the CLI without shutting down the service
    """
    async def run(self, *args, **kwargs):
        raise exceptions.Exit
    

class shutdown(baseCommand.BaseCommand):
    """
    @help: exit the CLI and shutdown the service
    """
    decorator = decorators.NeedsConfirmation()
    async def run(self, *args, **kwargs):
        raise exceptions.Shutdown
    
class whoami(baseCommand.BaseCommand):
    """
    @help: returns the username of the current user
    """
    async def run(self, verbose: bool, *args, **kwargs) -> str:
        user_info = self.t.authenticator.get_userinfo()
        if verbose:
            return str(user_info)
        return user_info.username