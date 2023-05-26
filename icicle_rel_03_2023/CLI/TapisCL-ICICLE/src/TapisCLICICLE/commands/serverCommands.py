import typing

from tapipy.tapis import Tapis


if __name__ != "__main__":
    from . import args as Args
    from . import baseCommand, decorators
    from utilities import exceptions


class switch_service(baseCommand.BaseCommand):
    """
    @help: switch the connected tapis service
    @todo: upgrade to federated auth
    """
    async def run(self, link: str, auth: str, *args, **kwargs):  # link is the baseURL
        if auth == "password":
            results = kwargs['server'].password_grant(link, kwargs['connection'])
        elif auth == "device_code":
            results = kwargs['server'].device_code_grant(link, kwargs['connection'])
        elif auth == "federated":
            results = kwargs['server'].federated_grant(link, kwargs['connection'])
        return results
      

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
    async def run(self, *args, **kwargs) -> str:
        user_info = self.t.authenticator.get_userinfo()
        return user_info
    

class get_args(baseCommand.BaseCommand):
    """
    @help: get the list of possible arguments 
    """
    async def run(self, *args, **kwargs):
        return Args.Args.argparser_args