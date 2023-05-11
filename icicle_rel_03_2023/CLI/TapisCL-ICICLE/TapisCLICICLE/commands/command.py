from typing import Callable, Optional, Union, Type
from abc import abstractmethod, ABC
import re
import inspect
from tapipy import tapis
try:
    from ..utilities.decorators import Auth, NeedsConfirmation, RequiresExpression, RequiresForm, SecureInput
    from ..utilities.decorators import exceptions
    from ..utilities.args import Args
    from ..utilities import helpers
except:
    import utilities.decorators as decorators
    import utilities.exceptions as exceptions
    import utilities.args as Args
    import utilities.helpers as helpers


class CommandMetaClass(type):
    def __new__(self, cls, name, bases, attrs):
        runner = attrs['run']
        for argument_name in helpers.get_parameters(runner):
            if argument_name not in list(Args.argparser_args.keys()):
                raise AttributeError(f"The argument {argument_name} in the run() method of the command '{name}' was not defined in the 'args' file")
        if '**kwargs' not in inspect.getfullargspec(runner).args:
            raise AttributeError(f"The run() method of the {name} class must have a **kwargs attribute to ignore misinput")
        return super().__new__(cls, name, bases, attrs)

    def help_string_retriever(self):
        try:
            docstring_components = self.__class__.__doc__
            docstring_components = docstring_components.split("@")
            for docstring_component in docstring_components:
                if re.match(r'^[^:]+', docstring_component).group(0) == "help":
                    return docstring_component.split("help: ")[1]
            raise Exception()
        except Exception as e:
            raise exceptions.HelpDoesNotExist(self.__class__.__name__)
        
class BaseCommand(ABC, metaclass=CommandMetaClass):
    decorator = None
    def __init__(self, t: tapis.Tapis):
        self.t = None
        self.help = self.__help_gen()
    
    def __argument_help_gen(self):
        arguments_str = ""
        for argument in helpers.get_parameters(self.run):
            arguments_str += f" {Args.argparser_args[argument]['args'][0]}/ \
                                {Args.argparser_args[argument]['args'][1]} \
                                <{argument}>"
    
    def __help_gen(self):
        return {
            "Command":self.__class__.__name__,
            "Description":self.help_string_retriever(),
            "Syntax":self.__argument_help_gen()
        }
        
    @abstractmethod
    async def run(self, **kwargs):
        pass

    async def __call__(self, **kwargs):
        if kwargs['help']:
            return self.help
        if self.decorator:
            return await self.decorator(self.run, connection=kwargs['connection'], **kwargs)
        return await self.run(**kwargs)
    

class BaseQuery(BaseCommand):
    def get_pod_credentials(self, id):
        uname, pword = self.t.pods.get_pod_credentials(pod_id=id).user_username, self.t.pods.get_pod_credentials(pod_id=id).user_password
        return uname, pword
    

class BaseCommandGroup(ABC, metaclass=CommandMetaClass):
    def __init__(self, t: tapis.Tapis, username: str, password: str, command_map: dict[str, BaseCommand]):
        self.command_map = command_map
        self.t = t
        self.username = username
        self.password = password
        self.brief_help = self.help_string_retriever()
        self.verbose_help = self.__help_gen()

    def __help_gen(self):
        verbose_help = dict()
        for command in self.command_map.values():
            verbose_help.update(**command)
        return verbose_help

    async def __call__(self, **kwargs):
        if kwargs['help'] and not kwargs['command']:
            return self.verbose_help
        try:
            command = self.command_map[kwargs['command']]
            result = await command(**kwargs)
            if type(result) == tapis.TapisResult:
                return str(result)
            return result
        except KeyError:
            raise KeyError(f"The command {kwargs['command']} does not exist. See help menu")
