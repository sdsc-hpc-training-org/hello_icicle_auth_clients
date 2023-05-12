from tapipy import tapis
import pyperclip
try:
    from .. import baseCommand
    from ...utilities import decorators
    from . import systemCommands
except:
    import baseCommand
    import utilities.decorators as decorators
    import systemCommands


class SystemCommandGroup(baseCommand.BaseCommandGroup):
    group_command_map = {
        'get_systems':systemCommands.get_systems,
        'get_system_info':systemCommands.get_system_info,
        'create_system':systemCommands.create_system,
        'set_credentials':systemCommands.system_credential_upload,
        'set_password':systemCommands.system_password_set,
        'delete_system':systemCommands.delete_system,
    }