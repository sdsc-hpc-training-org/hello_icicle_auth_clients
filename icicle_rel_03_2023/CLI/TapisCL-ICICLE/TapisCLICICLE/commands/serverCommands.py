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


class tapis_init(baseCommand.BaseCommand):
    """
    @help: switch the connected tapis service
    @todo: upgrade to federated auth
    """
    decorator = decorators.Auth()
    async def run(self, username: str, link: str, *args, **kwargs) -> tuple[typing.Any, str, str] | None:  # link is the baseURL
        start = time.time()
        self.username = username
        self.password = kwargs['password']
        try:
            t = Tapis(base_url=f"https://{link}",
                    username=username,
                    password=kwargs['password'])
            t.get_tokens()
        except Exception as e:
            print(e)
            raise exceptions.InvalidCredentialsReceived(function=self.tapis_init, cred_type="Tapis Auth")

        self.configure_decorators(self.username, self.password)
        # V3 Headers
        header_dat = {"X-Tapis-token": t.access_token.access_token,
                      "Content-Type": "application/json"}

        # Service URL
        url = f"{link}/v3"

        # create authenticator for tapis systems
        authenticator = t.access_token
        # extract the access token from the authenticator
        access_token = re.findall(
            r'(?<=access_token: )(.*)', str(authenticator))[0]
        
        if 'win' in sys.platform:
            os.system(f"set JWT={access_token}")
        else: # unix based
            os.system(f"export JWT={access_token}")

        self.update_credentials(t, username, kwargs['password'])

        self.t = t
        self.url = url
        self.access_token = access_token

        self.logger.info(f"initiated in {time.time()-start}")

        return f"Successfully initialized tapis service on {self.url}"
      

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
        self.logger.info("Shutdown initiated")
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