if __name__ != "__main__":
    from . import systemCommands, volumeCommands, serverCommands, appCommands, podCommands, fileCommands, dataFormatters, baseCommand
    from .query import postgres, neo4j
    from utilities import exceptions
    from commands.arguments.argument import Argument
    from commands.commandOpts import CHECK_EXPLICIT_ID


class Systems(baseCommand.BaseCommandMap):
    """
    @help: run operations on Tapis systems
    """
    data_formatter = dataFormatters.DataFormatters.system_formatter
    command_map = {
        'get_systems':systemCommands.get_systems(), # since initialization of commands is separate from __init__, you dont need to specify these as classes anymore
        'get_system_info':systemCommands.get_system_info(),
        'get_scheduler_profiles':systemCommands.get_scheduler_profiles(),
        'verify_pki_keys':systemCommands.verify_pki_keys(),
        'create_child_system':systemCommands.create_child_system(),
        'create_system':systemCommands.create_system(),
        'update_system':systemCommands.update_system(),
        'is_enabled':systemCommands.is_enabled(),
        'enable_system':systemCommands.enable_system(),
        'disable_system':systemCommands.disable_system(),
        'system':systemCommands.system(),
        'exit_system':systemCommands.exit_system(),
        'delete_system':systemCommands.delete_system(),
        'undelete_system':systemCommands.undelete_system()
    }


class Server(baseCommand.BaseCommandMap):
    """
    @help: run config operations on the 
    """
    data_formatter = dataFormatters.DataFormatters.server_formatter
    command_map = {
        'whoami':serverCommands.whoami(),
        'whereami':serverCommands.whereami(),
        'exit':serverCommands.exit(),
        'shutdown':serverCommands.shutdown(),
        "get_args":serverCommands.get_args(),
        'switch_service':serverCommands.switch_service()
    }


class Pods(baseCommand.BaseCommandMap):
    """
    @help: run operations on tapis pods
    """
    data_formatter = dataFormatters.DataFormatters.pod_formatter
    command_map = {
        'get_pods':podCommands.get_pods(),
        'get_pod':podCommands.get_pod(),
        'create_pod':podCommands.create_pod(),
        'update_pod':podCommands.update_pod(),
        'start_pod':podCommands.start_pod(),
        'restart_pod':podCommands.restart_pod(),
        'delete_pod':podCommands.delete_pod(),
        'set_pod_perms':podCommands.set_pod_perms(),
        'stop_pod':podCommands.stop_pod(),
        'delete_pod_perms':podCommands.delete_pod_perms(),
        'get_perms':podCommands.get_perms(),
        'copy_pod_password':podCommands.copy_pod_password(),
        'get_pod_logs':podCommands.get_pod_logs(),
    }


class Volumes(baseCommand.BaseCommandMap):
    """
    @help: run operations on tapis volumes and snapshots
    """
    command_map = {
        'get_volumes':volumeCommands.get_volumes(),
        'create_volume':volumeCommands.create_volume(),
        'get_volume':volumeCommands.get_volume(),
        'volume':volumeCommands.volume(),
        'update_volume':volumeCommands.update_volume(),
        'delete_volume':volumeCommands.delete_volume(),
        'dir':volumeCommands.dir(),
        'upload_volume':volumeCommands.upload_volume(),
        'set_volume_permission':volumeCommands.set_volume_permission(),
        'get_volume_permissions':volumeCommands.get_volume_permissions(),
        'delete_volume_permission':volumeCommands.delete_volume_permission(),
        'get_snapshots':volumeCommands.get_snapshots(),
        'create_snapshot':volumeCommands.create_snapshot(),
        'get_snapshot':volumeCommands.get_snapshot(),
        'update_snapshot':volumeCommands.update_snapshot(),
        'delete_snapshot':volumeCommands.delete_snapshot(),
        'list_snapshot_files':volumeCommands.list_snapshot_files()
    }


class Files(baseCommand.BaseCommandMap):
    """
    @help: run operations on tapis files
    """
    command_map = {
        'ls':fileCommands.ls(),
        'cd':fileCommands.cd(),
        'showme':fileCommands.showme(),
        'cat':fileCommands.cat(),
        'mkdir':fileCommands.mkdir(),
        'mv':fileCommands.mv(),
        'cp':fileCommands.cp(),
        'rm':fileCommands.rm(),
        'get_recent_transfers':fileCommands.get_recent_transfers(),
        'create_postit':fileCommands.create_postit(),
        'list_postits':fileCommands.list_postits(),
        'get_postit':fileCommands.get_postit(),
        'delete_postit':fileCommands.delete_postit(),
        'redeem_postit':fileCommands.redeem_postit(),
        'upload':fileCommands.upload(),
        'download':fileCommands.download(),
    }


class Apps(baseCommand.BaseCommandMap):
    """
    @help: Run operations on tapis apps
    """
    data_formatter = dataFormatters.DataFormatters.app_formatter
    command_map = {
        'create_app':appCommands.create_app(),
        'get_apps':appCommands.get_apps(),
        'delete_app':appCommands.delete_app(),
        'get_app':appCommands.get_app(),
        'assign_default_job_attributes':appCommands.assign_default_job_attributes(),
        'is_enabled':appCommands.is_enabled(),
        'enable_app':appCommands.enable_app(),
        'disable_app':appCommands.disable_app(),
        'undelete_app':appCommands.undelete_app(),
        'get_app_user_perms':appCommands.get_app_user_perms(),
        'grant_app_user_perms':appCommands.grant_app_user_perms(),
        'revoke_app_user_perms':appCommands.revoke_app_user_perms()
    }


class Query(baseCommand.BaseCommandMap):
    """
    @help: run integrated query CLIs
    """
    command_map = {
        'postgres': postgres.postgres(),
        'neo4j': neo4j.neo4j()
    }


class ArgsGenerator:
    def generate_truncated_arguments(self, arg_dict: dict) -> dict:
        truncation_dict = dict()
        for argument_name in arg_dict.keys():
            truncated_argument = self.__generate_truncated_argument(argument_name, truncation_dict)
            truncation_dict[argument_name] = truncated_argument
        return truncation_dict
            
    def __generate_truncated_argument(self, argument, truncated_arguments_dict, attempts=1):
        if argument[attempts-1] in ('_', '-'):
            argument += 1
        abbreviation = argument[:attempts]
        for index, letter in enumerate(argument):
            if letter.isupper() or not (argument[index-1].isnumeric() or argument[index-1].isalpha()):
                abbreviation += letter.lower()

        if abbreviation.lower() in list(truncated_arguments_dict.values()):
            abbreviation = self.__generate_truncated_argument(argument, truncated_arguments_dict, attempts=attempts+1)
        return abbreviation.lower()
    

class AggregateCommandMap(baseCommand.CommandContainer, ArgsGenerator):
    groups = {
        'Systems': Systems(),
        'Server': Server(),
        'Pods': Pods(),
        'Files': Files(),
        #'Apps': Apps(),
        'Query': Query(),
        'Volumes':Volumes()
    }
    def __init__(self):
        truncated_arguments = self.generate_truncated_arguments(self.arguments)
        for command in self.aggregate_command_map.values():
            command.update_args_with_truncated(truncated_arguments)
        for name, argument in self.arguments.items():
            argument.truncated_arg = truncated_arguments[name]
        self.help = self.__general_help()

    def __general_help(self):
        general_help = list()
        for group in self.groups.values():
            general_help.append(group.brief_help)
        return general_help

    def update_credentials(self, t, username, password):
        for command_name, command in self.aggregate_command_map.items():
            command.set_t_and_creds(t, username, password, self)

    async def run_command(self, connection, command_data: dict):
        """
        process and run command based on received kwargs
        """
        command_name = command_data['command_selection']

        if command_name in list(self.aggregate_command_map.keys()):
            command = self.aggregate_command_map[command_name]
            if command.supports_config_file and 'file' in list(command_data.keys()) and command_data['file']:
                command_data = {'file':command_data['file']}

            command_data['connection'] = connection
            command_data['server'] = self
            return await command(**command_data)
        elif command_name in list(self.groups.keys()):
            return self.groups[command_name]()
        elif command_name == "help":
            return self.help
        else:
            raise exceptions.CommandNotFoundError(command_name)