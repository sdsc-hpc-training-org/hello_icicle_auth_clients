from tapipy.tapis import TapisResult
import typing
import os
try:
    from ..utilities import helpers
    from ..utilities import decorators
except:
    import utilities.helpers as helpers 
    import utilities.decorators as decorators


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
server_path = os.path.join(__location__, '..\\server.py')


class tapisObject(helpers.OperationsHelper, decorators.DecoratorSetup, helpers.DynamicHelpUtility):
    def __init__(self, tapis_instance, username, password, connection=None, command_map=None):
        self.t = tapis_instance
        self.username = username
        self.password = password
        self.connection = connection

        self.command_map = command_map
        
        if self.command_map:
            self.help = self.help_generation()

    def __call__(self, **kwargs):
        command = self.command_map[kwargs['command']]
        kwargs = self.filter_kwargs(command, kwargs)
        result = command(**kwargs)
        if type(result) == TapisResult:
            return str(result)
        return result
    
    def help(self, name: typing.Optional[str]):
        """
        @help: get help information for the command group
        """
        if name:
            return self.help[name]
        return self.help
    

class TapisQuery(tapisObject):
    def __init__(self, tapis_object, uname, pword, connection=None):
        super().__init__(tapis_object, uname, pword, connection=connection)
        self.t = tapis_object
        self.__code__ = self.query.__code__

    def __call__(self, **kwargs):
        kwargs = self.filter_kwargs(self.query, kwargs)
        result = self.query(**kwargs)
        return result
        
    def get_credentials(self, id):
        uname, pword = self.t.pods.get_pod_credentials(pod_id=id).user_username, self.t.pods.get_pod_credentials(pod_id=id).user_password
        return uname, pword