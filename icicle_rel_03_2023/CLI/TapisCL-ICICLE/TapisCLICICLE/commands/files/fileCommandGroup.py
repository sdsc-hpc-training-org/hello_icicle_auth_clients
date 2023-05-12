from tapipy import tapis
import pyperclip
try:
    from .. import baseCommand
    from ...utilities import decorators
    from . import fileCommands
except:
    import baseCommand
    import utilities.decorators as decorators
    import fileCommands


class FileCommandGroup(baseCommand.BaseCommandGroup):
    group_command_map = {
                'list_files':fileCommands.list_files,
                'upload':fileCommands.upload,
                'download':fileCommands.download,
            }