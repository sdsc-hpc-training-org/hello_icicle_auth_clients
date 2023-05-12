from tapipy import tapis
import pyperclip
try:
    from .. import baseCommand
    from ...utilities import decorators
    from . import appCommands
except:
    import baseCommand
    import utilities.decorators as decorators
    import appCommands


class AppCommandGroup(baseCommand.BaseCommandGroup):
    group_command_map = {
                'create_app':appCommands.create_app,
                'get_apps':appCommands.get_apps,
                'delete_app':appCommands.delete_app,
                'get_app_info':appCommands.get_app,
                'run_app':appCommands.run_job,
                'get_app_status':appCommands.get_job_status,
                'download_app_results':appCommands.download_job_output,
            }