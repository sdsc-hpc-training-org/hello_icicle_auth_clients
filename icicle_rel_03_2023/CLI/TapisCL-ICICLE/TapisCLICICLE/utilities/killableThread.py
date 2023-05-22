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

    