import typing
import sys
import threading
from TypeEnforcement.type_enforcer import TypeEnforcer
import re
import json
import argparse
try:
    from . import exceptions
    from . import args
except:
    import exceptions
    import args


command_parameters = args.Args.argparser_args


def get_parameters(func):
    args = func.__code__.co_varnames[:func.__code__.co_argcount]
    if args[0] == "self":
        args = args[1:]
    return args

class OperationsHelper:
    def filter_kwargs(self, func: typing.Callable, kwargs: dict) -> dict:
        filtered = dict()
        variables = list(get_parameters(func))
        for arg in variables:
            filtered.update({arg:kwargs[arg]})
        return filtered
    

class DynamicHelpUtility:
    """
    dynamically generate the help menu based on the doc  string and function arguments using .__doc__ and .__code__
    to generate helps for each command, iterate over the command map of the selected tapis wrapper object, and generate separate help menu for each
    """
    def __locate_docstring_help(self, func: typing.Callable | object, command_name: str) -> str:
        docstring_components = func.__doc__
        if docstring_components:
            docstring_components = docstring_components.split("@")
        else:
            raise exceptions.HelpDoesNotExist(command_name)
        for docstring_component in docstring_components:
            if re.match(r'^[^:]+', docstring_component).group(0) == "help":
                return docstring_component.split("help: ")[1]
        else:
            raise exceptions.HelpDoesNotExist(command_name)
        
    def __server_commands_help_gen(self, map: dict) -> dict:
        help = dict()
        for command_name, command in map.items():
            command_help = dict()
            command_help['command_name'] = command_name
            command_help['description'] = self.__locate_docstring_help(command, command_name)
            if map == self.command_map:
                help_str = f"{self.__class__.__name__.lower()}"
            else:
                help_str = f"{self.__class__.__name__.lower()} -c help"
            command_help['syntax'] = help_str
            help[command_name] = command_help
        return help

    def __tapis_service_commands_help_gen(self) -> dict:
        help_menu = dict()
        for command_name, command in self.command_map.items():
            command_help = dict()
            command_help['command_name'] = command_name
            command_help['description'] = self.__locate_docstring_help(command, command_name)
            arguments = get_parameters(command)
            argument_help = f"{self.__class__.__name__.lower()} -c {command_name}"
            for argument in arguments:
                if argument != "password":
                    argument_help += f" {command_parameters[argument]['args'][1]} <{argument}>"
            command_help['syntax'] = argument_help
            help_menu[command_name] = command_help
        return help_menu
            
    def help_generation(self) -> dict:
        if self.__class__.__name__ != 'Server': 
            return self.__tapis_service_commands_help_gen()
        else:
            return self.__server_commands_help_gen(map=self.command_group_map).update(self.__server_commands_help_gen(map=self.command_map))
    

class KillableThread(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run     
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


if __name__ == "__main__":
    class Silly:
        def z(self, y=True, x=False):
            return None
    x = OperationsHelper()
    v=Silly()
    x.filter_kwargs(v.z, {'y':False, 'x':"True", 'z':"hi"})
    