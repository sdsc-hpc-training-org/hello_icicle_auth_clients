import re
import inspect
import abc
import ast
import json
from typing import Type
import typing
from abc import abstractmethod, ABC
import os
from pprint import pprint

from commands import decorators # I finally understand. Imported at the top level by serverRun, so it can only see packages from that vantage point
from utilities import exceptions
from commands.arguments.argument import Argument, DynamicChoiceList, ALLOWED_ARG_TYPES
from socketopts import schemas
from commands import dataFormatters


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(f"{__file__}")))
saved_command = os.path.join(__location__, r'entered_command.json')


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


class HelpMenu:
    def __init__(self, required_arguments: dict[str, Argument], optional_arguments: dict[str, Argument]):
        self.required_arguments = required_arguments
        self.optional_arguments = optional_arguments
        self.arguments = {**required_arguments, **optional_arguments}
        self.help = self.create_help_menu()

    def create_help_menu(self):
        help_dict = {'required':dict(), 'optional':dict()}
        for arg_name, argument in self.required_arguments.items():
            help_dict['required'][arg_name] = argument.help_message()
        for arg_name, argument in self.optional_arguments.items():
            help_dict['optional'][arg_name] = argument.help_message()
        return help_dict
    
    def dict(self):
        return self.arguments


class BaseCommand(ABC, HelpStringRetriever, metaclass=CommandMetaClass):
    decorator = None
    return_fields: list = []
    command_opt: list = None
    supports_config_file: bool = False
    required_arguments: list[Argument] | dict = list()
    optional_arguments: list[Argument] | dict = list()
    def __init__(self):
        self.t = None
        self.username = None
        self.password = None
        self.server = None
        self.arguments = dict()
        self.return_formatter: dataFormatters.BaseDataFormatter = dataFormatters.BaseDataFormatter(self.return_fields)
        self.default_commands()
        if self.supports_config_file:
            self.optional_arguments.append(Argument('file'))
        if isinstance(self.required_arguments, list):
            self.required_arguments = {argument.argument:argument for argument in self.required_arguments}
            self.arguments.update(**self.required_arguments)
        if isinstance(self.optional_arguments, list):  
            self.optional_arguments = {argument.argument:argument for argument in self.optional_arguments}
            self.arguments.update(**self.optional_arguments)
        self.positional_arguments = [arg_name for arg_name, arg in self.required_arguments.items() if arg.positional]
        self.form_arguments = [arg_name for arg_name, arg in self.arguments.items() if arg.arg_type not in  ('standard', 'silent')]
        self.help: dict[dict[str, list[dict[str, str]]]] = dict()

        self.command_execution_sequence = []
        if self.supports_config_file:
            self.command_execution_sequence.append(self.handle_config_file)
        if self.positional_arguments:
            self.command_execution_sequence.append(self.check_for_positionals)
        if self.command_opt:
            self.command_execution_sequence.append(self.handle_arg_opts)
        self.command_execution_sequence.append(self.verify_argument_rules_followed)
        if self.form_arguments:
            self.command_execution_sequence.append(self.handle_form_input)
        self.command_execution_sequence.append(self.verify_argument_rules_followed)
        self.command_execution_sequence.append(self.filter_kwargs)

    def default_commands(self):
        default_commands = [Argument('connection', arg_type='silent'),
                            Argument('verbose', arg_type='silent'),
                            Argument('help', arg_type='silent'),
                            Argument('positionals', arg_type='silent')]
        
        for command in default_commands:
            self.required_arguments.append(command)

    async def verify_argument_rules_followed(self, kwargs):
        print("ACTIVATED THE ARGUMENT RULES TESTER")
        for name, value in self.arguments.items():
            if name in self.required_arguments and kwargs[name] == None:
                raise Exception(f"The argument {name} is required by the command {self.__class__.__name__}")
            elif name in kwargs and name in self.required_arguments and name not in self.form_arguments:
                kwargs[name] = self.required_arguments[name].verify_standard_value(kwargs[name])
            elif name in kwargs and name in self.optional_arguments and name not in self.form_arguments:
                kwargs[name] = self.optional_arguments[name].verify_standard_value(kwargs[name])
        return kwargs

    async def filter_kwargs(self, kwargs):
        filtered_kwargs = dict()
        for arg, value in kwargs.items():
            if arg in self.arguments and value or arg in self.required_arguments or (value == False and arg in self.arguments and self.arguments[arg].arg_type == 'standard'):
                filtered_kwargs[arg] = value
        return filtered_kwargs

    async def handle_config_file(self, kwargs):
        if kwargs['file']:
            with open(kwargs['file'], 'r') as f:
                kwargs = json.loads(f.read)
        return kwargs
    
    async def handle_form_input(self, kwargs):
        for arg_name in self.form_arguments:
            if kwargs[arg_name] or arg_name in self.required_arguments:
                request = schemas.FormRequest(request_content={arg_name:self.arguments[arg_name] for arg_name in self.form_arguments if kwargs[arg_name] or arg_name in self.required_arguments})
                await kwargs['connection'].send(request)
                response: schemas.FormResponse = await kwargs['connection'].receive()
                kwargs.update(**response.request_content)
        return kwargs
    
    async def handle_arg_opts(self, kwargs):
        for opt in self.command_opt:
            kwargs = opt(kwargs)
        return kwargs
    
    async def check_for_positionals(self, kwargs):
        for arg_name, value in zip(self.positional_arguments, kwargs['positionals']):
            kwargs[arg_name] = value
        return kwargs

    def set_t_and_creds(self, t, username, password, server):
        self.t = t
        self.username = username
        self.password = password
        self.server = server
        for key, arg in self.optional_arguments.items():
            if issubclass(arg.choices.__class__, DynamicChoiceList):
                arg.choices = arg.choices(self.t)

    def update_args_with_truncated(self, truncated_args_dict):
        try:
            for key in self.required_arguments:
                self.required_arguments[key].truncated_arg = f"-{truncated_args_dict[key]}"
            for key in self.optional_arguments:
                self.optional_arguments[key].truncated_arg = f"-{truncated_args_dict[key]}"
            self.help['required'] = self.__argument_help_compiler(self.required_arguments)
            self.help['optional'] = self.__argument_help_compiler(self.optional_arguments)
        except Exception as e:
            print(self.__class__.__name__)
            raise e
        
    def __argument_help_compiler(self, arg_dict: dict[str, Argument]):
        verbose_dict = dict()
        standard_str = str()
        for name, argument in arg_dict.items():
            if not (name in self.required_arguments and name in self.form_arguments) and argument.arg_type != 'silent':
                verbose_dict[name] = argument.help_message()
                standard_str += argument.str()
        return {'verbose':verbose_dict, 'standard':standard_str}

    def __get_help(self, verbose):
        help_dict = {"Command":self.__class__.__name__,
                    "Description":self.help_string_retriever()}
        if not verbose:
            help_dict.update(**{
                "Syntax":f"{self.__class__.__name__} {self.help['required']['standard']}\n(Optional Arguments) {self.help['optional']['standard']}"})
        else:
            help_dict.update(**{
                "Syntax":f"{self.__class__.__name__}",
                "Required Arguments":self.help['required']['verbose'],
                "Optional Arguments":self.help['optional']['verbose']})
        return help_dict
    
    def brief_help(self):
        return {"Command":self.__class__.__name__,
                "Description":self.help_string_retriever()}
    
    @abstractmethod
    async def run(self, *args, **kwargs):
        pass

    async def __call__(self, **kwargs):
        pprint(kwargs)
        if self.decorator:
            try:
                return_value = await self.decorator(input_command=self, **kwargs)
            except (ValueError, exceptions.NoConfirmationError) as e:
                return f"Command execution failed due to {e}"

        if kwargs['help']:
            return self.__get_help(verbose=kwargs['verbose'])
        for handler in self.command_execution_sequence:
            print(f"EXECUTING: {handler.__name__}")
            kwargs = await handler(kwargs)
            pprint(f"{kwargs}\n")
        else:
            try:
                return_value = await self.run(**kwargs)
            except exceptions.Shutdown as e:
                raise e
            except Exception as e:
                with open(saved_command, 'a') as f:
                    kwargs.pop('connection')
                    f.write(json.dumps(kwargs))
                    print(f"Argument input failure, command data written to file {saved_command}")
                    raise e
        if self.return_formatter:
            return_value = self.return_formatter(return_value, kwargs['verbose'])
        else:
            return_value = str(return_value)
        return return_value
    

class BaseQuery(BaseCommand):
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
            instance.__special_command_opts(name, attrs)
        return instance
    
    def __check_commands_are_proper_type(self, name, attrs):
        commands = attrs['command_map']
        if not commands:
            raise AttributeError(f"The command group {name} has no commands!")
            
    def __check_command_name(self, name, attrs):
        commands = attrs['command_map']
        for command_name, command in commands.items():
            if command_name != command.__class__.__name__:
                raise AttributeError(f"The command {command_name} in the command map {name} is a different name from its corresponding command class, {command.__class__.__name__}")

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
    command_opt = None
    def __init__(self):
        self.brief_help = self.__brief_help_gen()
        self.verbose_help = self.__help_gen()
        for name, command in self.command_map.items():
            self.aggregate_command_map.update({name:command})
            if command.required_arguments or command.optional_arguments:
                self.__contribute_to_arguments(command)

    def __contribute_to_arguments(self, command):
        arg_dict = {**command.required_arguments, **command.optional_arguments}
        for name, arg in arg_dict.items():
            if name not in self.arguments:
                self.arguments[name] = arg
            elif self.arguments[name].check_for_copy_data() != arg.check_for_copy_data():
                raise ValueError(f"Found two instances of the argument {arg.argument} that had different attributes.\n\n{command.__class__.__name__}: {arg.check_for_copy_data()}\n\nvs\n\n{self.arguments[name].check_for_copy_data()}")

    def __help_gen(self):
        verbose_help = list()
        for command in self.command_map.values():
            verbose_help.append(command.brief_help())
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
