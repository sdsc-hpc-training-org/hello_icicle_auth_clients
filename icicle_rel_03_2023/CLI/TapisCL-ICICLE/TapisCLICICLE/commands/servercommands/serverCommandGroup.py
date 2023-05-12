from tapipy import tapis
import pyperclip
try:
    from .. import baseCommand
    from ...utilities import decorators
    from . import serverCommands
except:
    import baseCommand
    import utilities.decorators as decorators
    import serverCommands


class ServerCommandGroup(baseCommand.BaseCommandGroup):
    group_command_map = {
            'whoami':serverCommands.whoami,
            'exit':serverCommands.exit,
            'shutdown':serverCommands.shutdown,
            'switch_service':serverCommands.tapis_init
    }