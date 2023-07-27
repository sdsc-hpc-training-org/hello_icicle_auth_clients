from .Apps import appCommands
from .Systems import systemCommands
import pprint


if __name__ != "__main__":
    from . import authenticatorClients, snapshotCommands, volumeCommands, serverCommands, podCommands, fileCommands, dataFormatters, baseCommand, jobCommands
    from .query import postgres, neo4j
    from utilities import exceptions
    from commands.arguments.argument import Argument
    from commands.commandOpts import CHECK_EXPLICIT_ID


class Systems(baseCommand.BaseCommandMap):
    """
    @help: run operations on Tapis systems
    """
    command_map = {
        'get_systems':systemCommands.get_systems(), # since initialization of commands is separate from __init__, you dont need to specify these as classes anymore
        'get_system':systemCommands.get_system(),
        'get_scheduler_profiles':systemCommands.get_scheduler_profiles(),
        'create_scheduler_profile':systemCommands.create_scheduler_profile(),
        'delete_scheduler_profile':systemCommands.delete_scheduler_profile(),
        'submit_system_credentials':systemCommands.submit_system_credentials(),
        'verify_pki_keys':systemCommands.verify_pki_keys(),
        'create_system':systemCommands.create_system(),
        'create_s3_system':systemCommands.create_s3_system(),
        'update_system':systemCommands.update_system(),
        'update_s3_system':systemCommands.update_s3_system(),
        'is_system_enabled':systemCommands.is_system_enabled(),
        'enable_system':systemCommands.enable_system(),
        'disable_system':systemCommands.disable_system(),
        'system':systemCommands.system(),
        'exit_system':systemCommands.exit_system(),
        'delete_system':systemCommands.delete_system(),
        'undelete_system':systemCommands.undelete_system(),
        'create_child_system':systemCommands.create_child_system(),
        'unlink_child_system':systemCommands.unlink_child_system(),
        'unlink_children':systemCommands.unlink_children(),
        'get_user_perms':systemCommands.get_user_perms(),
        'grant_user_perms':systemCommands.grant_user_perms(),
        'revoke_user_perms':systemCommands.revoke_user_perms(),
    }


class General(baseCommand.BaseCommandMap):
    """
    @help: run config operations on the 
    """
    command_map = {
        'get_tenants':serverCommands.get_tenants(),
        'get_tenant':serverCommands.get_tenant(),
        'whoami':serverCommands.whoami(),
        'user':serverCommands.user(),
        'whereami':serverCommands.whereami(),
        'exit':serverCommands.exit(),
        'shutdown':serverCommands.shutdown(),
        'switch_tenant_to':serverCommands.switch_tenant_to(),
        'manpages':serverCommands.manpages()
    }


class Pods(baseCommand.BaseCommandMap):
    """
    @help: run operations on tapis pods
    """
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
        'get_pod_perms':podCommands.get_pod_perms(),
        'get_pod_credentials':podCommands.get_pod_credentials(),
        'get_pod_uri':podCommands.get_pod_uri(),
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
        'exit_volume':volumeCommands.exit_volume(),
        'update_volume':volumeCommands.update_volume(),
        'delete_volume':volumeCommands.delete_volume(),
        'dir':volumeCommands.dir(),
        'upload_volume':volumeCommands.upload_volume(),
        'set_volume_permission':volumeCommands.set_volume_permission(),
        'get_volume_permissions':volumeCommands.get_volume_permissions(),
        'delete_volume_permission':volumeCommands.delete_volume_permission(),
    }


class Snapshots(baseCommand.BaseCommandMap):
    """
    @help: commands to deal with snapshots
    """
    command_map = {
        'get_snapshots':snapshotCommands.get_snapshots(),
        'create_snapshot':snapshotCommands.create_snapshot(),
        'get_snapshot':snapshotCommands.get_snapshot(),
        'update_snapshot':snapshotCommands.update_snapshot(),
        'delete_snapshot':snapshotCommands.delete_snapshot(),
        'list_snapshot_files':snapshotCommands.list_snapshot_files()
    }


class AuthClients(baseCommand.BaseCommandMap):
    """
    @help: manage auth clients to be used on your own applications
    """
    command_map = {
        'list_clients': authenticatorClients.list_clients(),
        'create_client': authenticatorClients.create_client(),
        'get_client': authenticatorClients.get_client(),
        'update_client': authenticatorClients.update_client(),
        'delete_client': authenticatorClients.delete_client()
    }

class Files(baseCommand.BaseCommandMap):
    """
    @help: run operations on tapis files
    """
    command_map = {
        'ls':fileCommands.ls(),
        'cd':fileCommands.cd(),
        'pwd':fileCommands.pwd(),
        'showme':fileCommands.showme(),
        'cat':fileCommands.cat(),
        'mkdir':fileCommands.mkdir(),
        'mv':fileCommands.mv(),
        'cp':fileCommands.cp(),
        'rm':fileCommands.rm(),
        'get_permissions':fileCommands.get_permissions(),
        'grant_permissions':fileCommands.grant_permissions(),
        'delete_permissions':fileCommands.delete_permissions(),
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
    command_map = {
        'create_app':appCommands.create_app(),
        'update_app':appCommands.update_app(),
        'get_apps':appCommands.get_apps(),
        'delete_app':appCommands.delete_app(),
        'get_app':appCommands.get_app(),
        'assign_default_job_attributes':appCommands.assign_default_job_attributes(),
        'is_app_enabled':appCommands.is_app_enabled(),
        'enable_app':appCommands.enable_app(),
        'disable_app':appCommands.disable_app(),
        'undelete_app':appCommands.undelete_app(),
        'get_app_history':appCommands.get_app_history(),
        'get_app_user_perms':appCommands.get_app_user_perms(),
        'grant_app_user_perms':appCommands.grant_app_user_perms(),
        'revoke_app_user_perms':appCommands.revoke_app_user_perms()
    }


class Jobs(baseCommand.BaseCommandMap):
    """
    @help: run jobs on a tapis system
    """
    command_map = {
        'hide_job':jobCommands.hide_job(),
        'unhide_job':jobCommands.unhide_job(),
        'cancel_job':jobCommands.cancel_job(),
        'get_job':jobCommands.get_job(),
        'get_job_history':jobCommands.get_job_history(),
        'get_jobs':jobCommands.get_jobs(),
        'download_job_output':jobCommands.download_job_output(),
        'get_job_status':jobCommands.get_job_status(),
        'get_job_last_message':jobCommands.get_job_last_message(),
        'resubmit_job':jobCommands.resubmit_job(),
        'submit_job':jobCommands.submit_job(),
        'share_job':jobCommands.share_job(),
        'get_job_share':jobCommands.get_job_share(),
        'delete_job_share':jobCommands.delete_job_share(),
        'subscribe_to_job':jobCommands.subscribe_to_job(),
        'get_subscriptions':jobCommands.get_subscriptions(),
        'delete_subscriptions':jobCommands.delete_subscriptions()
    }


class Query(baseCommand.BaseCommandMap):
    """
    @help: run integrated query CLIs
    """
    command_map = {
        'postgres': postgres.postgres(),
        'neo4j': neo4j.neo4j(),
        'get_neo4j_pod_uri':neo4j.get_neo4j_pod_uri(),
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
        'General': General(),
        'Pods': Pods(),
        'Files': Files(),
        'Apps': Apps(),
        'Query': Query(),
        'Volumes':Volumes(),
        'Jobs': Jobs(),
        'Snapshots': Snapshots(),
        'AuthClients': AuthClients()
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
        if command_name in self.aggregate_command_map:
            command = self.aggregate_command_map[command_name]
            command_data['connection'] = connection
            kwargs = dict()
            for argument, value in command_data.items():
                if argument in command.arguments:
                    kwargs[argument] = value
            pprint.pprint(kwargs)
            return await command(**kwargs)
        elif command_name in self.groups:
            return self.groups[command_name]()
        elif command_name == "help":
            return self.help
        else:
            raise exceptions.CommandNotFoundError(command_name)