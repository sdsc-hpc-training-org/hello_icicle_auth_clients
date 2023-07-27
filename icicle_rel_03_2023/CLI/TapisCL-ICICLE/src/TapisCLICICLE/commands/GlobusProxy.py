import pyperclip
from tapipy.tapis import errors as TapisErrors


if __name__ != "__main__":
    from . import baseCommand, decorators
    from .arguments import argument
    Argument = argument.Argument


