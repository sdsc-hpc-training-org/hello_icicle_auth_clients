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
    import exceptions as exceptions
    import args as args


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

    def print_response(self, response_message):
        """
        format response messages from the server
        """
        if type(response_message) == dict:
            self.recursive_dict_print(response_message)
        elif (type(response_message) == list or 
             type(response_message) == tuple or 
             type(response_message) == set):
            for value in response_message:
                print(value)
        else:
            print(response_message)

    