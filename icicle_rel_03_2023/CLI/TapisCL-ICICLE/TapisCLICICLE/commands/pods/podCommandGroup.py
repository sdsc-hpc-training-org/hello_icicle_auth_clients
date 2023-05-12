from tapipy import tapis
import pyperclip
try:
    from .. import baseCommand
    from ...utilities import decorators
    from . import podCommands
except:
    import baseCommand
    import utilities.decorators as decorators
    import podCommands


class PodCommandGroup(baseCommand.BaseCommandGroup):
    group_command_map = {
        'get_pods':podCommands.get_pods,
        'create_pod':podCommands.create_pod,
        'start_pod':podCommands.start_pod,
        'restart_pod':podCommands.restart_pod,
        'delete_pod':podCommands.delete_pod,
        'set_pod_perms':podCommands.set_pod_perms,
        'stop_pod':podCommands.stop_pod,
        'delete_pod_perms':podCommands.delete_pod_perms,
        'get_perms':podCommands.get_perms,
        'copy_pod_password':podCommands.copy_pod_password,
        'get_logs':podCommands.get_pod_logs,
    }