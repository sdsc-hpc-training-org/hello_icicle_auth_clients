import pyperclip
from tapipy.tapis import errors as TapisErrors


if __name__ != "__main__":
    from . import baseCommand, decorators
    from .arguments import argument
    Argument = argument.Argument


class get_pods(baseCommand.BaseCommand):
    """
    @help: return a list of pods the current tapis instance has access to
    """
    async def run(self, *args, **kwargs) -> str: 
        pods_list = self.t.pods.get_pods()
        return pods_list


class get_pod(baseCommand.BaseCommand):
    """
    @help: return a specific pod based on pod_id
    """
    required_arguments=[
        Argument('pod_id')
    ]
    async def run(self, *args, **kwargs) -> str: 
        pod_data = self.t.pods.get_pod(pod_id=kwargs["pod_id"])
        return pod_data


class create_pod(baseCommand.BaseCommand):
    """
    @help: create a new pod on the selected Tapis service
    """
    supports_config_file=True
    required_arguments=[
        Argument('pod_id'),
        Argument('pod_template')
    ]
    optional_arguments=[
        Argument('description', arg_type='str_input'),
        Argument('command', arg_type='input_list'),
        Argument('evnironment_variables', arg_type='input_dict'),
        Argument('data_request', arg_type='input_list'),
        Argument('roles_required', arg_type='input_list'),
        Argument('time_to_stop_default', data_type='int'),
        Argument('time_to_stop_instance', data_type='int'),
        Argument('volume_mounts', arg_type='input_dict', data_type=argument.Form(
            'property_name', arguments_list = [
                Argument('type'),
                Argument("mount_path"),
                Argument('sub_path')
            ]
        )),
        Argument('networking', arg_type='input_dict', data_type=argument.Form(
            'property_name', arguments_list = [
                Argument('protocol'),
                Argument('port'),
                Argument('url')
            ]
        )),
        Argument('resources', arg_type='input_dict', data_type=argument.Form(
            'property_name', arguments_list = [
                Argument('cpu_request'),
                Argument('cpu_limit'),
                Argument('mem_request'),
                Argument('mem_limit'),
            ]
        ))
    ]
    async def run(self, *args, **kwargs) -> str:
        template_name = kwargs['template']
        template_formats = (f"template/{template_name}", f"{self.username}/{template_name}", template_name)
        for template_format in template_formats:
            try:
                kwargs['template'] = template_format
                pod_information = self.t.pods.create_pod(**kwargs)
                break
            except TapisErrors.BadRequestError as e:
                if template_format != template_formats[-1]:
                    continue
                raise ValueError(f"Failed to execute pod creation due to {str(e)}")
        return pod_information
    

class update_pod(create_pod):
    """
    @help: update a pod. Must be restarted to stage changes
    """
    required_arguments=[
        Argument('pod_id'),
    ]
    async def run(self, *args, **kwargs):
        pod_information = self.t.pods.update_pod(**kwargs)
        return pod_information


class start_pod(baseCommand.BaseCommand):
    """
    @help: start the pod specified with pod_id
    """
    required_arguments=[
        Argument('pod_id'),
    ]
    async def run(self, *args, **kwargs):
        return_information = self.t.pods.start_pod(pod_id=kwargs['pod_id'])
        return return_information


class restart_pod(baseCommand.BaseCommand):
    """
    @help: initiate a pod restart
    """
    decorator=decorators.NeedsConfirmation()
    required_arguments=[
        Argument('pod_id'),
    ]
    async def run(self, *args, **kwargs) -> str:
        return_information = self.t.pods.restart_pod(pod_id=kwargs['pod_id'])
        return return_information


class stop_pod(baseCommand.BaseCommand):
    """
    @help: stop a pod's operations
    """
    decorator=decorators.NeedsConfirmation()
    required_arguments=[
        Argument('pod_id'),
    ]
    async def run(self, *args, **kwargs):
        return_information = self.t.pods.stop_pod(pod_id=kwargs['pod_id'])
        return return_information


class delete_pod(baseCommand.BaseCommand):
    """
    @help: delete select pod
    """
    decorator=decorators.NeedsConfirmation()
    required_arguments=[
        Argument('pod_id'),
    ]
    async def run(self, *args, **kwargs) -> str: 
        return_information = self.t.pods.delete_pod(pod_id=kwargs['pod_id'])
        return return_information
    

class set_pod_perms(baseCommand.BaseCommand):
    """
    @help: set the permissions for the pod selected
    """
    required_arguments=[
        Argument('pod_id'),
        Argument('username'),
        Argument('level')
    ]
    async def run(self, *args, **kwargs) -> str: # set pod permissions, given a pod pod_id, user, and permission level
        return_information = self.t.pods.set_pod_permission(pod_id=kwargs['pod_id'], user=kwargs['username'], level=kwargs['level'])
        return return_information


class delete_pod_perms(baseCommand.BaseCommand):
    """
    @help: delete the selected pod from the pods service you are connected to
    """
    decorator=decorators.NeedsConfirmation()
    required_arguments=[
        Argument('pod_id'),
        Argument('username')
    ]
    async def run(self, *args, **kwargs) -> str: # take away someones perms if they are being malicious, or something
        return_information = self.t.pods.delete_pod_perms(pod_id=kwargs['pod_id'], user=kwargs['username'])
        return return_information


class get_perms(baseCommand.BaseCommand):
    """
    @help: get the permissions list for the selected pod
    """
    required_arguments=[
        Argument('pod_id'),
    ]
    async def run(self, *args, **kwargs) -> str: # return a list of permissions on a given pod
        return_information = self.t.pods.get_pod_permissions(pod_id=kwargs['pod_id'])
        return return_information


class copy_pod_password(baseCommand.BaseCommand):
    """
    @help: copy the pod password to the clipboard
    """
    decorator=decorators.Auth()
    required_arguments=[
        Argument('pod_id'),
    ]
    async def run(self, *args, **kwargs) -> str: # copies the pod password to clipboard so that the user can access the pod via the neo4j desktop app. Maybe a security risk? not as bad as printing passwords out!
        password = self.t.pods.get_pod_credentials(pod_id=kwargs['pod_id']).user_password
        pyperclip.copy(password)
        password = None
        return 'copied to clipboard'


class get_pod_logs(baseCommand.BaseCommand):
    """
    @help: retrieve the logs of an active pod and either print them to the console, or write them to the specified file
    """
    required_arguments=[
        Argument('pod_id')
    ]
    optional_arguments=[
        Argument('destination_file')
    ]
    async def run(self, *args, **kwargs):
        logs = self.t.pods.get_pod_logs(pod_id=kwargs['pod_id'])
        file = kwargs['destination_file']
        if file:
            with open(file, 'w') as f:
                f.write(logs)
            return f"Log saved at {file}"
        return logs
    

