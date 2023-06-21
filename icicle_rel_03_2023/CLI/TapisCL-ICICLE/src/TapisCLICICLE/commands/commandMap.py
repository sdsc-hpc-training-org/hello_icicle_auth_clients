if __name__ != "__main__":
    from . import systemCommands, serverCommands, appCommands, podCommands, fileCommands, dataFormatters, baseCommand
    from .query import postgres, neo4j
    from utilities import exceptions
    from commands.arguments.argument import Argument


def CHECK_EXPLICIT_SYSTEM(kwargs):
    if not kwargs['id']:
        kwargs['id'] = kwargs['connection'].system
    return kwargs

class Systems(baseCommand.BaseCommandMap):
    """
    @help: run operations on Tapis systems
    """
    command_opt = [CHECK_EXPLICIT_SYSTEM]
    data_formatter = dataFormatters.DataFormatters.system_formatter
    command_map = {
        'get_systems':systemCommands.get_systems(), # since initialization of commands is separate from __init__, you dont need to specify these as classes anymore
        'get_system_info':systemCommands.get_system_info(),
        'get_scheduler_profiles':systemCommands.get_scheduler_profiles(),
        'create_child_system':systemCommands.create_child_system(),
        'create_system':systemCommands.create_system(),
        'system':systemCommands.system(),
        'exit_system':systemCommands.exit_system(),
        'delete_system':systemCommands.delete_system(),
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


class Files(baseCommand.BaseCommandMap):
    """
    @help: run operations on tapis files
    """
    command_opt = [CHECK_EXPLICIT_SYSTEM]
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
        'run_job':appCommands.run_job(),
        'get_job_status':appCommands.get_job_status(),
        'download_job_output':appCommands.download_job_output(),
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
            
    def __generate_truncated_argument(self, argument, truncated_arguments_dict, attempt=1):
        if argument[attempt-1] in ('_', '-'):
            attempt += 1
        truncated_argument = argument[:attempt]
        if truncated_argument in list(truncated_arguments_dict.values()):
            return self.__generate_truncated_argument(argument, truncated_arguments_dict, attempt=attempt+1)
        return truncated_argument
    

class AggregateCommandMap(baseCommand.CommandContainer, ArgsGenerator):
    groups = {
        'Systems': Systems(),
        'Server': Server(),
        'Pods': Pods(),
        'Files': Files(),
        #'Apps': Apps(),
        'Query': Query(),
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