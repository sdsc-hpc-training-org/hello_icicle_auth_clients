import re
import inspect
import abc
from typing import Type
from abc import abstractmethod, ABC

from commands import decorators # I finally understand. Imported at the top level by serverRun, so it can only see packages from that vantage point
from commands import args as Args
from utilities import exceptions


EXCLUDED_ARGUMENTS = ('self', 'args', 'kwargs')


def get_kwargs(function):
    sig = inspect.signature(function)
    keyword_args = [param.name for param in sig.parameters.values() if param.default != inspect.Parameter.empty]
    return keyword_args

def get_args(function):
    sig = inspect.signature(function)
    positional_args = [param.name for param in sig.parameters.values() if param.default == inspect.Parameter.empty]
    return positional_args


class HelpStringRetriever:
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
    

class CommandMetaClass(abc.ABCMeta):
    def __new__(cls, name, bases, attrs):
        instance = super().__new__(cls, name, bases, attrs)
        if name not in ('BaseQuery', 'BaseCommand'):
            instance.__check_run(name, attrs)
            instance.__check_command_args(name, attrs)
            instance.__check_decorator(name, attrs)
        return instance
    
    def __check_run(self, name, attrs):
        if 'run' not in list(attrs.keys()):
            raise AttributeError(f"The command {name} requires a 'run()' method")
        elif not inspect.iscoroutinefunction(attrs['run']):
            raise AttributeError(f"The run method of the command {name} must be a coroutine")
    
    def __check_command_args(self, name, attrs):
        args = get_args(attrs['run'])
        for argument_name in args:
            if argument_name not in list(Args.Args.argparser_args.keys()) and argument_name not in EXCLUDED_ARGUMENTS:
                raise AttributeError(f"The argument {argument_name} in the run() method of the command '{name}' was not defined in the 'args' file")
        if 'kwargs' not in args or 'args' not in args:
            raise AttributeError(f"The run() method of the {name} class must have a **kwargs and *args attribute to ignore misinput")
        
    def __check_decorator(self,name, attrs):
        if 'decorator' in list(attrs.keys()) and type(attrs['decorator']) not in decorators.DECORATOR_LIST:
            raise AttributeError(f"The decorator parameter of the command {name} is invalid. Must be set to None or to a decorator type. Currently is {type(attrs['decorator'])}")


class BaseCommand(ABC, HelpStringRetriever, metaclass=CommandMetaClass):
    decorator = None
    return_formatter = None
    def __init__(self):
        self.t = None
        self.username = None
        self.password = None
        self.server = None
        self.command_opt = None
        self.keyword_arguments = get_kwargs(self.run)
        self.positional_arguments = get_args(self.run)
        self.help = self.__help_gen()

    def set_t_and_creds(self, t, username, password, server):
        self.t = t
        self.username = username
        self.password = password
        self.server = server
    
    def __argument_help_gen(self):
        arguments_str = ""
        for argument in self.positional_arguments:
            if argument not in EXCLUDED_ARGUMENTS:
                arguments_str += f" {Args.Args.argparser_args[argument]['args'][0]}/{Args.Args.argparser_args[argument]['args'][1]} <{argument}>"
        if not arguments_str:
            arguments_str = "<No Arguments>"
        return arguments_str
    
    def __help_gen(self):
        return {
            "Command":self.__class__.__name__,
            "Description":self.help_string_retriever(),
            "Syntax":f"{self.__class__.__name__} {self.__argument_help_gen()}"
        }

    @abstractmethod
    async def run(self, *args, **kwargs):
        pass

    async def __call__(self, **kwargs):
        if self.command_opt:
            kwargs = self.command_opt(kwargs)
        if 'help' in list(kwargs.keys()) and kwargs['help']:
            return self.help
        if self.decorator:
            return_value = await self.decorator(self, **kwargs)
        else:
            return_value = await self.run(**kwargs)
        if self.return_formatter:
            return_value = self.return_formatter(return_value, kwargs['verbose'])
        return return_value
    

class BaseQuery(BaseCommand):
    decorator = None
    def get_pod_credentials(self, id):
        uname, pword = self.t.pods.get_pod_credentials(pod_id=id).user_username, self.t.pods.get_pod_credentials(pod_id=id).user_password
        return uname, pword
    
    @abstractmethod
    async def run(self, *args, **kwargs):
        pass
    

class CommandMapMetaClass(type):
    def __new__(cls, name, bases, attrs):
        instance = super().__new__(cls, name, bases, attrs)
        if name not in ('CommandMapMetaClass', 'BaseCommandMap'):
            instance.__check_commands_are_proper_type(name, attrs)
            instance.__check_command_name(name, attrs)
            instance.__check_data_formatter(name, attrs)
            instance.__special_command_opts(name, attrs)
        return instance
    
    def __check_commands_are_proper_type(self, name, attrs):
        commands = attrs['command_map']
        if not commands:
            raise AttributeError(f"The command group {name} has no commands!")
        for command_name, command in commands.items():
            if not issubclass(command.__class__, BaseCommand):
                raise AttributeError(f"The command {command_name} was not passed to the {name} as a class, but as an object. Ensure you do not instantiate commands when defining the class")
            
    def __check_command_name(self, name, attrs):
        commands = attrs['command_map']
        for command_name, command in commands.items():
            if command_name != command.__class__.__name__:
                raise AttributeError(f"The command {command_name} in the command map {name} is a different name from its corresponding command class, {command.__class__.__name__}")
            
    def __check_data_formatter(self, name, attrs):
        if 'data_formatter' not in list(attrs.keys()):
            print(f"WARNING: The command map {name} has no data formatter. If any commands have non json-serializable return values, command execution will fail! These must be handled by a formatter")

    def __special_command_opts(self, name, attrs):
        if 'command_opt' in list(attrs.keys()):
            for command_name, command in attrs['command_map']:
                command.command_opt = attrs['command_opt']


class CommandContainer:
    aggregate_command_map: dict[str, Type[BaseCommand]] = dict()


class BaseCommandMap(CommandContainer, HelpStringRetriever, metaclass=CommandMapMetaClass):
    command_map: dict[str, Type[BaseCommand]] = None
    data_formatter = None
    command_opt = None
    def __init__(self):
        self.brief_help = self.__brief_help_gen()
        self.verbose_help = self.__help_gen()
        for name, command in self.command_map.items():
            command.return_formatter = self.data_formatter
            self.aggregate_command_map.update({name:command})

    def __help_gen(self):
        verbose_help = dict()
        for command in self.command_map.values():
            verbose_help.update({command.__class__.__name__:command.help})
        return verbose_help
    
    def __brief_help_gen(self):
        brief_help = {
            'group':self.__class__.__name__,
            'description':self.help_string_retriever(),
            'instruction':f"enter {self.__class__.__name__} to retrieve list of commands"
        }
        return brief_help
    
    def __call__(self):
        return self.verbose_help
