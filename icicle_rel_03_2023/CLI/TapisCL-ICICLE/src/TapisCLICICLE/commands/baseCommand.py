import re
import inspect
import abc
import ast
import json
from typing import Type
from abc import abstractmethod, ABC

from commands import decorators # I finally understand. Imported at the top level by serverRun, so it can only see packages from that vantage point
from commands.arguments import args as Args
from utilities import exceptions
from commands.arguments.argument import Argument, DynamicChoiceList


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
            instance.__check_command_opt(name, attrs)
        return instance
    
    def __check_run(self, name, attrs):
        if 'run' not in list(attrs.keys()):
            raise AttributeError(f"The command {name} requires a 'run()' method")
        elif not inspect.iscoroutinefunction(attrs['run']):
            raise AttributeError(f"The run method of the command {name} must be a coroutine")
    
    def __check_command_args(self, name, attrs):
        run_params = get_args(attrs['run'])
        args = attrs['required_arguments'] + attrs['optional_arguments']
        for argument in args:
            if not issubclass(argument.__class__, Argument) and not isinstance(argument, Argument):
                raise AttributeError(f"The argument {argument.argument} of the command '{name}' must be of type 'Argument'")
            if argument in attrs['optional_arguments'] and argument.positional:
                raise AttributeError(f"The optional argument {argument.argument} of the command {name} cannot be positional. All positional arguments must be required")
        if 'kwargs' not in run_params or 'args' not in run_params:
            raise AttributeError(f"The run() method of the {name} class must have a **kwargs and *args as parameters")
        
    def __check_decorator(self, name, attrs):
        if 'decorator' in list(attrs.keys()) and type(attrs['decorator']) not in decorators.DECORATOR_LIST:
            raise TypeError(f"The decorator parameter of the command {name} is invalid. Must be set to None or to a decorator type. Currently is {type(attrs['decorator'])}")
        
    def __check_command_opt(self, name, attrs):
        if 'command_opt' in list(attrs.keys()) and type((attrs['command_opt'])) != list:
            raise TypeError(f"The command opt attribute of the command {name} must be a list!")


class BaseCommand(ABC, HelpStringRetriever, metaclass=CommandMetaClass):
    decorator = None
    return_formatter = None
    command_opt: list = None
    supports_config_file: bool = False
    required_arguments: list[Argument] = list()
    optional_arguments: list[Argument] = list()
    def __init__(self):
        self.t = None
        self.username = None
        self.password = None
        self.server = None
        self.arg_names = [argument.argument for argument in self.required_arguments + self.optional_arguments]
        self.help: dict[dict[str, list[dict[str, str]]]] = dict()

    def set_t_and_creds(self, t, username, password, server):
        self.t = t
        self.username = username
        self.password = password
        self.server = server

    def __argument_list_help_compiler(self, arg_list: list[Argument]):
        return [{"help":f"{argument.truncated_arg}/{argument.full_arg} <{argument.argument}>",
          "description":argument.description} 
         for argument in arg_list]

    def update_args_with_truncated(self, aggregate_args_dict):
        for index, arg in enumerate(self.required_arguments):
            self.required_arguments[index] = aggregate_args_dict[arg.argument]
        for index, arg in enumerate(self.optional_arguments):
            if issubclass(aggregate_args_dict[arg.argument].choices.__class__, DynamicChoiceList):
                aggregate_args_dict[arg.argument].choices = aggregate_args_dict[arg.argument].choices(self.t)
            self.required_arguments[index] = aggregate_args_dict[arg.argument]
        self.help['required'] = self.__argument_list_help_compiler(self.required_arguments)
        self.help['optional'] = self.__argument_list_help_compiler(self.optional_arguments)
    
    def __get_help(self, verbose):
        help_dict = {"Command":self.__class__.__name__,
                    "Description":self.help_string_retriever()}
        if not verbose:
            help_dict.update(**{
                "Syntax":f"{self.__class__.__name__} {[arg_help['help'] for arg_help in self.help['required']]}",
                "Optional Arguments":[arg_help['help'] for arg_help in self.help['optional']]
            })
        else:
            help_dict.update(**{
                "Syntax":f"{self.__class__.__name__} {self.help['required']}",
                "Optional Arguments":self.help['optional']
            })
        return help_dict

    @abstractmethod
    async def run(self, *args, **kwargs):
        pass

    def run_command_opts(self, **kwargs):
        if self.command_opt:
            for opt in self.command_opt:
                kwargs = opt(kwargs)
        return kwargs

    async def __call__(self, **kwargs):
        verbose = kwargs.pop('verbose')
        help = kwargs.pop('help')
        if help:
            return self.__get_help(verbose=verbose)
        
        elif self.supports_config_file and 'file' in list(kwargs['keys']):
            with open(kwargs['file'], 'r') as f:
                kwargs = json.loads(f.read)
        
        kwargs = self.run_command_opts(**kwargs)

        if self.decorator:
            return_value = await self.decorator(self, **kwargs)
        else:
            return_value = await self.run(**kwargs)
        if self.return_formatter:
            return_value = self.return_formatter(return_value, verbose)
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
            if type(attrs['command_opt']) != list:
                raise TypeError(f"The command_opt attribute for the command group {name} must be a list!")
            for command_name, command in attrs['command_map'].items():
                if not command.command_opt:
                    command.command_opt = attrs['command_opt']
                    continue
                command.command_opt += attrs['command_opt']


class CommandContainer:
    aggregate_command_map: dict[str, Type[BaseCommand]] = dict()
    arguments : dict[str, Argument]= {
        'help':Argument('help', action='store_true'),
        'verbose':Argument('verbose', action='store_true'),
        'file':Argument('file')
    }


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
            self.__contribute_to_arguments(command)

    def __contribute_to_arguments(self, command):
        arg_list = command.required_arguments + command.optional_arguments
        for arg in arg_list:
            if arg.argument not in list(self.arguments.keys()):
                self.arguments[arg.argument] = arg
            elif self.arguments[arg.argument].json() != arg.json():
                raise ValueError(f"Found two instances of the argument {arg.argument} that had different attributes")

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
