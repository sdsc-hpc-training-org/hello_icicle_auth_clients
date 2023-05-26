if __name__ != "__main__":
    from . import systemCommands, serverCommands, appCommands, podCommands, fileCommands, dataFormatters, baseCommand
    from .query import postgres, neo4j
    from utilities import exceptions


class Systems(baseCommand.BaseCommandMap):
    """
    @help: run operations on Tapis systems
    """
    data_formatter = dataFormatters.DataFormatters.system_formatter
    command_map = {
        'get_systems':systemCommands.get_systems(), # since initialization of commands is separate from __init__, you dont need to specify these as classes anymore
        'get_system_info':systemCommands.get_system_info(),
        'create_system':systemCommands.create_system(),
        'set_system_credentials':systemCommands.set_system_credentials(),
        'set_system_password':systemCommands.set_system_password(),
        'delete_system':systemCommands.delete_system(),
    }


class Server(baseCommand.BaseCommandMap):
    """
    @help: run config operations on the 
    """
    data_formatter = dataFormatters.DataFormatters.server_formatter
    command_map = {
        'whoami':serverCommands.whoami(),
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
    command_map = {
        'list_files':fileCommands.list_files(),
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


class AggregateCommandMap(baseCommand.CommandContainer):
    groups = {
        'Systems': Systems(),
        'Server': Server(),
        'Pods': Pods(),
        'Files': Files(),
        'Apps': Apps(),
        'Query': Query(),
    }
    def __init__(self):
        self.help = self.__general_help()

    def __general_help(self):
        general_help = list()
        for group in self.groups.values():
            general_help.append(group.brief_help)
        return general_help

    def update_credentials(self, t, username, password):
        for command_name, command in self.aggregate_command_map.items():
            command.set_t_and_creds(t, username, password)

    async def run_command(self, connection, command_data: dict):
        """
        process and run command based on received kwargs
        """
        command_data['connection'] = connection
        command_data['server'] = self
        print(f"FROM RUN COMMAND {command_data}")
        command_name = command_data['command']
        if command_name in list(self.aggregate_command_map.keys()):
            command = self.aggregate_command_map[command_name]
            command_data.pop('command')
            return await command(**command_data)
        elif command_name in list(self.groups.keys()):
            return self.groups[command_name]()
        elif command_name == "help":
            return self.help
        else:
            raise exceptions.CommandNotFoundError(command_name)