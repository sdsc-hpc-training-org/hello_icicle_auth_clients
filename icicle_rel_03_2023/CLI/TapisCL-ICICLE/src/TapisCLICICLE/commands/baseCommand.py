import re
import inspect
import abc
import ast
import json
from typing import Type
import typing
from abc import abstractmethod, ABC

from commands import decorators # I finally understand. Imported at the top level by serverRun, so it can only see packages from that vantage point
from utilities import exceptions
from commands.arguments.argument import Argument, DynamicChoiceList, ALLOWED_ARG_TYPES
from socketopts import schemas


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
        args = []
        if 'required_arguments' in list(attrs.keys()): 
            args += attrs['required_arguments']
        if 'optional_arguments' in list(attrs.keys()): 
            args += attrs['optional_arguments']
        if args:
            for argument in args:
                if not issubclass(argument.__class__, Argument) and not isinstance(argument, Argument):
                    raise AttributeError(f"The argument {argument.argument} of the command '{name}' must be of type 'Argument'")
                if 'optional_arguments' in list(attrs.keys()) and argument in attrs['optional_arguments'] and argument.positional:
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
    required_arguments: list[Argument] | dict = list()
    optional_arguments: list[Argument] | dict = list()
    def __init__(self):
        self.t = None
        self.username = None
        self.password = None
        self.server = None
        self.arg_names = [argument.argument for argument in self.required_arguments] + [argument.argument for argument in self.optional_arguments]
        self.arguments = dict()
        if isinstance(self.required_arguments, list):
            self.required_arguments = {argument.argument:argument for argument in self.required_arguments}
            self.arguments.update(**self.required_arguments)
        if isinstance(self.optional_arguments, list):  
            self.optional_arguments = {argument.argument:argument for argument in self.optional_arguments}
            self.arguments.update(**self.optional_arguments)
        self.positional_arguments = [arg_name for arg_name, arg in self.required_arguments.items() if arg.positional]
        self.help: dict[dict[str, list[dict[str, str]]]] = dict()

    def set_t_and_creds(self, t, username, password, server):
        self.t = t
        self.username = username
        self.password = password
        self.server = server
        for key, arg in self.optional_arguments.items():
            if issubclass(arg.choices.__class__, DynamicChoiceList):
                arg.choices = arg.choices(self.t)

    def update_args_with_truncated(self, aggregate_args_dict):
        try:
            for key, arg in self.required_arguments.items():
                self.required_arguments[key] = aggregate_args_dict[key]
            for key, arg in self.optional_arguments.items():
                self.optional_arguments[key] = aggregate_args_dict[key]
            self.help['required'] = self.__argument_list_help_compiler(self.required_arguments)
            self.help['optional'] = self.__argument_list_help_compiler(self.optional_arguments)
        except Exception as e:
            print(self.__class__.__name__)
            raise e
        
    def __argument_list_help_compiler(self, arg_dict: dict):
        argument_help_dict = dict()
        for name, argument in arg_dict.items():
            if argument.positional:
                arg_help = {name:f"<{argument.argument}>",
                "description":argument.description}
            elif argument.action != 'store':
                arg_help = {name:f"{argument.truncated_arg}/{argument.full_arg}",
                "description":argument.description}
            else:
                arg_help = {name:f"{argument.truncated_arg}/{argument.full_arg} <{argument.argument}>",
                "description":argument.description}
            argument_help_dict[name] = arg_help
        return argument_help_dict
    
    def __non_verbose_help_string_creator(self, help_dict):
        help_string = ""
        for arg_name, arg_help in help_dict.items():
            help_string += f"{arg_help[arg_name]}\n"
        return help_string

    def __get_help(self, verbose):
        help_dict = {"Command":self.__class__.__name__,
                    "Description":self.help_string_retriever()}
        if not verbose:
            help_dict.update(**{
                "Syntax":f"{self.__class__.__name__} {self.__non_verbose_help_string_creator(self.help['required'])}",
                "Optional Arguments":self.__non_verbose_help_string_creator(self.help['optional'])
            })
        else:
            help_dict.update(**{
                "Syntax":f"{self.__class__.__name__}",
                "Required Arguments":self.help['required'],
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
    
    def check_commands_for_special_requests(self, kwargs):
        require_further_input = dict()
        for name, arg in kwargs.items():
            if arg and name in list(self.arguments.keys()) and self.arguments[name].arg_type in typing.get_args(ALLOWED_ARG_TYPES):
                require_further_input[name] = arg.json()
        return require_further_input
    
    def check_for_positionals(self, kwargs):
        for arg_name, value in zip(self.positional_arguments, kwargs['positionals']):
            kwargs[arg_name] = value
        return kwargs

    async def __call__(self, **kwargs):
        verbose = kwargs.pop('verbose')
        help = kwargs.pop('help')
        command = kwargs.pop('command')
        if help:
            return self.__get_help(verbose=verbose)
        
        elif self.supports_config_file and 'file' in list(kwargs.keys()):
            with open(kwargs['file'], 'r') as f:
                kwargs = json.loads(f.read)

        kwargs = self.check_for_positionals(kwargs)

        require_further_input = self.check_commands_for_special_requests(kwargs)
        if require_further_input:
            request = schemas.FormRequest(request_content=require_further_input)
            await kwargs['connection'].send(request)
            response: schemas.FormResponse = await kwargs['connection'].receive()
            kwargs.update(**response.request_content)

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
            if command.required_arguments or command.optional_arguments:
                self.__contribute_to_arguments(command)

    def __contribute_to_arguments(self, command):
        arg_dict = {**command.required_arguments, **command.optional_arguments}
        for name, arg in arg_dict.items():
            if name not in list(self.arguments.keys()):
                self.arguments[name] = arg
            elif self.arguments[name].json() != arg.json():
                raise ValueError(f"Found two instances of the argument {arg.argument} that had different attributes.\n\n{command.__class__.__name__}: {arg.json()}\n\nvs\n\n{self.arguments[name].json()}")

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
