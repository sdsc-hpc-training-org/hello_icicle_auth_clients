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
    from commands import apps, files, pods, query, systems
except:
    import utilities.helpers as helpers
    import utilities.exceptions as exceptions
    import utilities.decorators as decorators
    import utilities.args as args
    import utilities.decorators as decorators
    import utilities.schemas as schemas
    import commands.apps as apps
    import commands.files as files
    import commands.pods as pods
    import commands.query as query
    import commands.systems as systems


class ServerCommands(decorators.DecoratorSetup, helpers.DynamicHelpUtility):  
    def __init__(self):
        self.pods = None
        self.systems = None
        self.files = None
        self.apps = None
        self.neo4j = None
        self.postgres = None
        self.t = None
        self.url = None
        self.access_token = None
        self.username = None
        self.password = None
        self.help_menu = None

        self.command_group_map = None
        self.command_map = None

    def commands_initializer(self):
        # instantiate the subsystems
        self.command_group_map = {
            'pods':self.pods,
            'systems':self.systems,
            'files':self.files,
            'apps':self.apps,
        }
        self.command_map = {
            'help':self.help,
            'whoami':self.whoami,
            'exit':self.exit,
            'shutdown':self.shutdown,
            'neo4j':self.neo4j,
            'postgres':self.postgres,
            'switch_service':self.tapis_init
        }
        help0, help1 = self.help_generation()
        self.help_menu = dict(help0, **help1)
        print(self.help_menu)

    @decorators.Auth
    def tapis_init(self, username: str, password: str, link: str, connection=None) -> tuple[typing.Any, str, str] | None:  # link is the baseURL
        """
        @help: switch the connected tapis service
        """
        start = time.time()
        self.username = username
        self.password = password
        try:
            t = Tapis(base_url=link,
                    username=username,
                    password=password)
            t.get_tokens()
        except:
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

        self.pods = pods.Pods(t, username, password)
        self.systems = systems.Systems(t, username, password)
        self.files = files.Files(t, username, password)
        self.apps = apps.Apps(t, username, password)
        self.neo4j = query.Neo4jCLI(t, username, password)
        self.postgres = query.PostgresCLI(t, username, password)

        self.t = t
        self.url = url
        self.access_token = access_token

        self.logger.info(f"initiated in {time.time()-start}")

        return f"Successfully initialized tapis service on {self.url}"
      
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
        elif command in self.help_menu:
            return self.help_menu[command]
        return self.help_menu
    
    def whoami(self, verbose: bool, connection=None) -> str:
        """
        @help: returns the username of the current user
        """
        user_info = self.t.authenticator.get_userinfo()
        if verbose:
            return str(user_info)
        return user_info.username