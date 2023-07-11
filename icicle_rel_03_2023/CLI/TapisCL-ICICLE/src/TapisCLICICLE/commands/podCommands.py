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
    return_fields = ['pod_id', 'pod_template', 'status']
    async def run(self, *args, **kwargs) -> str: 
        pods_list = self.t.pods.get_pods()
        return pods_list


class get_pod(baseCommand.BaseCommand):
    """
    @help: return a specific pod based on pod_id
    """
    return_fields = ['pod_id', 'pod_template', 'status']
    required_arguments=[
        Argument('pod_id', positional=True)
    ]
    async def run(self, *args, **kwargs) -> str: 
        pod_data = self.t.pods.get_pod(pod_id=kwargs["pod_id"])
        return pod_data


class create_pod(baseCommand.BaseCommand):
    """
    @help: create a new pod on the selected Tapis service
    @doc: fix the pod updating, make sure non selected optional vaiables do not overwrite. Why description appending???
    """
    return_fields = ['pod_id', 'pod_template', 'status']
    supports_config_file=True
    required_arguments=[
        Argument('pod_id', positional=True),
        Argument('pod_template', positional=True)
    ]
    optional_arguments=[
        Argument('description', arg_type='str_input', size_limit=(0, 2048)),
        Argument('command', arg_type='input_list', data_type=argument.Argument('command', arg_type='str_input')),
        Argument('environment_variables', arg_type='input_dict', data_type=argument.Argument('environment_variable', arg_type='str_input')),
        Argument('data_request', arg_type='input_list', data_type=argument.Argument('data_request', arg_type='str_input')),
        Argument('roles_required', arg_type='input_list', data_type=argument.Argument('required_role', arg_type='str_input')),
        Argument('time_to_stop_default', data_type='int'),
        Argument('time_to_stop_instance', data_type='int'),
        Argument('volume_mounts', arg_type='input_dict', data_type=argument.Form(
            'volume_mount', arguments_list = [
                Argument('type', choices=['tapisvolume', 'tapissnapshot', 'pvc']),
                Argument("mount_path"),
                Argument('sub_path')
            ]
        )),
        Argument('networking', arg_type='input_dict', data_type=argument.Form(
            'network', arguments_list = [
                Argument('protocol'),
                Argument('port', data_type='int'),
                Argument('url')
            ]
        )),
        argument.Form(
            'resources', arguments_list = [
                Argument('cpu_request', data_type='int'),
                Argument('cpu_limit', data_type='int'),
                Argument('mem_request', data_type='int'),
                Argument('mem_limit', data_type='int'),
            ]
        )
    ]
    async def run(self, *args, **kwargs) -> str:
        template_name = kwargs['pod_template']
        template_formats = (f"template/{template_name}", f"{self.username}/{template_name}", template_name)
        for template_format in template_formats:
            try:
                kwargs['pod_template'] = template_format
                pod_information = self.t.pods.create_pod(**kwargs)
                break
            except TapisErrors.BadRequestError as e:
                if template_format != template_formats[-1]:
                    continue
                raise ValueError(f"Failed to execute pod creation due to {str(e)}")
        return pod_information
    

class PodUpdatingRetriever(baseCommand.UpdatableFormRetriever):
    def __call__(self, tapis_instance, **kwargs):
        pod_data = tapis_instance.pods.get_pod(pod_id=kwargs["pod_id"])
        return pod_data
    

class update_pod(create_pod): # make it so the command retrieves current settings and sends them over so forms can append and edit instead of just overwrite
    """
    @help: update a pod. Must be restarted to stage changes
    """
    updateable_form_retriever=PodUpdatingRetriever()
    return_fields = ['pod_id', 'pod_template', 'status']
    required_arguments=[
        Argument('pod_id', positional=True),
    ]
    async def run(self, *args, **kwargs):
        print(kwargs)
        pod_information = self.t.pods.update_pod(**kwargs)
        return pod_information


class start_pod(baseCommand.BaseCommand):
    """
    @help: start the pod specified with pod_id
    """
    return_fields = ['pod_id', 'pod_template', 'status']
    required_arguments=[
        Argument('pod_id', positional=True),
    ]
    async def run(self, *args, **kwargs):
        return_information = self.t.pods.start_pod(pod_id=kwargs['pod_id'])
        return return_information


class restart_pod(baseCommand.BaseCommand):
    """
    @help: initiate a pod restart
    """
    return_fields = ['pod_id', 'pod_template', 'status']
    decorator=decorators.NeedsConfirmation()
    required_arguments=[
        Argument('pod_id', positional=True),
    ]
    async def run(self, *args, **kwargs) -> str:
        return_information = self.t.pods.restart_pod(pod_id=kwargs['pod_id'])
        return return_information


class stop_pod(baseCommand.BaseCommand):
    """
    @help: stop a pod's operations
    """
    return_fields = ['pod_id', 'pod_template', 'status']
    decorator=decorators.NeedsConfirmation()
    required_arguments=[
        Argument('pod_id', positional=True),
    ]
    async def run(self, *args, **kwargs):
        return_information = self.t.pods.stop_pod(pod_id=kwargs['pod_id'])
        return str(return_information)


class delete_pod(baseCommand.BaseCommand):
    """
    @help: delete select pod
    """
    return_fields = ['pod_id', 'pod_template', 'status']
    decorator=decorators.NeedsConfirmation()
    required_arguments=[
        Argument('pod_id', positional=True),
    ]
    async def run(self, *args, **kwargs) -> str: 
        return_information = self.t.pods.delete_pod(pod_id=kwargs['pod_id'])
        return str(return_information)
    

class set_pod_perms(baseCommand.BaseCommand):
    """
    @help: set the permissions for the pod selected
    """
    return_fields = ['permissions']
    required_arguments=[
        Argument('pod_id', positional=True),
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
    return_fields = ['permissions']
    decorator=decorators.NeedsConfirmation()
    required_arguments=[
        Argument('pod_id', positional=True),
        Argument('username')
    ]
    async def run(self, *args, **kwargs) -> str: # take away someones perms if they are being malicious, or something
        return_information = self.t.pods.delete_pod_perms(pod_id=kwargs['pod_id'], user=kwargs['username'])
        return return_information


class get_pod_perms(baseCommand.BaseCommand):
    """
    @help: get the permissions list for the selected pod
    """
    return_fields = ['permissions']
    required_arguments=[
        Argument('pod_id', positional=True),
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
        Argument('pod_id', positional=True),
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
    return_fields = ['logs']
    required_arguments=[
        Argument('pod_id', positional=True)
    ]
    optional_arguments=[
        Argument('destination_file')
    ]
    async def run(self, *args, **kwargs):
        logs = self.t.pods.get_pod_logs(pod_id=kwargs['pod_id'])
        if 'destination_file' in kwargs:
            file = kwargs['destination_file']
        else:
            file = None
        if file:
            with open(file, 'w') as f:
                f.write(logs)
            return f"Log saved at {file}"
        return logs
    

