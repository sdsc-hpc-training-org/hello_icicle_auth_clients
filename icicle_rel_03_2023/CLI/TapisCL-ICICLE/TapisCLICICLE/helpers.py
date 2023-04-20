"""
HELPERS
Aggregation of helper functions and classes
"""
import typing
import sys
import threading
import re
try:
    from . import exceptions
    from . import args
except:
    import exceptions
    import args


command_parameters = args.Args.argparser_args


def get_parameters(func):
    args = list(func.__code__.co_varnames[:func.__code__.co_argcount])
    if args[0] == "self":
        args = args[1:]
    return args

class OperationsHelper:
    """
    filters the kwargs received by the server to prevent an error from happening
    """
    def filter_kwargs(self, func: typing.Callable, kwargs: dict) -> dict:
        filtered = dict()
        variables = list(get_parameters(func))
        for arg in variables:
            if arg in command_parameters: filtered.update({arg:kwargs[arg]})
            else: filtered.update({arg:None})
        return filtered

    def print_dict(self, dict_):
        for key, value in dict_.items():
            print(f"{key}: {value}")
    

class DynamicHelpUtility:
    """
    dynamically generate the help menu based on the doc  string and function arguments using .__doc__ and .__code__
    to generate helps for each command, iterate over the command map of the selected tapis wrapper object, and generate separate help menu for each
    """
    def __locate_docstring_help(self, func: typing.Callable | object, command_name: str) -> str:
        """
        extract @help from the docstring
        """
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

    def __tapis_service_commands_help_gen(self, map) -> dict:
        """
        generate help menu based on the parameters of the function and the docstring
        """
        help_menu = dict()
        for command_name, command in map.items():
            command_help = dict()
            command_help['command_name'] = command_name
            command_help['description'] = self.__locate_docstring_help(command, command_name)
            arguments = None
            if self.__class__.__name__ != 'Server': 
                argument_help = f"{self.__class__.__name__.lower()} -c {command_name}"
                arguments = get_parameters(command)
            else:
                if map == self.command_map:
                    argument_help = f"{command_name}"
                    arguments = get_parameters(command)
                else:
                    argument_help = f"{command_name} -c help"
            if arguments:
                for argument in arguments:
                    if argument in args.Args.argparser_args:
                        argument_help += f" {command_parameters[argument]['args'][1]} <{argument}>"

            command_help['syntax'] = argument_help
            help_menu[command_name] = command_help
        return help_menu
            
    def help_generation(self) -> dict:
        """
        generate different help menu based on the classname
        """
        if self.__class__.__name__ != 'Server': 
            return self.__tapis_service_commands_help_gen(map=self.command_map)
        else:
            return self.__tapis_service_commands_help_gen(map=self.command_group_map), self.__tapis_service_commands_help_gen(map=self.command_map)
    

class KillableThread(threading.Thread):
    """
    Extends the threading.Thread class from python threading library. Used for the loading animation
    """
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


class Formatters:
    """
    Format received dictionaries in the client code
    """
    def recursive_dict_print(self, input_data: dict, depth: int=0):
        for key, value in input_data.items():
            if isinstance(value, dict):
                print(("  " * depth) + f"{key}:")
                self.recursive_dict_print(value, depth=depth + 1)
            elif isinstance(value, (list, tuple, set)):
                print(("  " * depth) + f"{key}:")
                for data in value:
                    print(("  " * (depth + 1)) + data)
            else: 
                print(("  " * depth) + f"{key}: {str(value).strip()}")
        if depth == 1:
            print("\n")


if __name__ == "__main__":
    class Silly:
        def z(self, y=True, x=False):
            return None
    x = OperationsHelper()
    v=Silly()
    x.filter_kwargs(v.z, {'y':False, 'x':"True", 'z':"hi"})
    