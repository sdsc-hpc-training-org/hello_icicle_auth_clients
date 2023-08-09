import pyperclip
import pprint
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
    @help: create a new pod. Pods are non persistent and have limited lives by default. You can either set them to live forever by setting time to stop to -1, or have them backup to a volume mount
    """
    return_fields = ['pod_id', 'pod_template', 'status']
    supports_config_file=True
    required_arguments=[
        Argument('pod_id', positional=True),
        Argument('pod_template', positional=True),
    ]
    optional_arguments=[
        Argument('volume_mounts', arg_type='input_dict', data_type=argument.Form(
            'volume_mount', required_arguments = [
                Argument('type', choices=['tapisvolume', 'tapissnapshot', 'pvc']),
                Argument("mount_path", description='This is top level path you want to mount the volume on inside the pod. This is something like <neo4j-home>\data for a neo4j pod. Data from that path will load to the mount and become persistent')
            ],
            optional_arguments = [
                Argument('sub_path', description='If you want to only load a single file, like file.txt (which is inside the parent mount path) you can specify here')
            ]
        ), description="Used to attach the pod to an existing kubernetes volume to provide pod persistence (in case of crash). Each key is the volume_id"),
        Argument('description', arg_type='str_input', size_limit=(0, 2048)),
        Argument('command', arg_type='input_list', data_type=argument.Argument('command', arg_type='str_input'), description="Command to run in the pod"),
        Argument('environment_variables', arg_type='input_dict', data_type=argument.Argument('environment_variable', arg_type='str_input')),
        Argument('roles_required', arg_type='input_list', data_type=argument.Argument('required_role', arg_type='str_input'), description='what role is required by the user to access this pod?'),
        Argument('time_to_stop_default', data_type='int', description='set to -1 to run forever'),
        Argument('time_to_stop_instance', data_type='int', description='set to -1 to run forever'),
        Argument('networking', arg_type='input_dict', data_type=argument.Form(
            'network', required_arguments = [
                Argument('protocol', default_value='http', description='Something like https'),
                Argument('port', data_type='int', default_value=5000),
                Argument('url')
            ]
        ), description='Important networking configuration. You probably shouldnt touch this, but I wont stop you'),
        argument.Form(
            'resources', required_arguments = [
                Argument('cpu_request', data_type='int', default_value=250),
                Argument('cpu_limit', data_type='int', default_value=2000),
                Argument('mem_request', data_type='int', default_value=256),
                Argument('mem_limit', data_type='int', default_value=3072),
            ]
        )
    ]
    async def run(self, *args, **kwargs) -> str:
        template_name = kwargs['pod_template']
        template_formats = (f"template/{template_name}", f"{self.username}/{template_name}", template_name)
        if 'volume_mounts' in kwargs and kwargs['volume_mounts']:
            for mount_name, mount in kwargs['volume_mounts'].items():
                if mount['type'] == 'tapisvolume':
                    try:
                        self.t.pods.get_volume(volume_id=mount_name)
                    except:
                        self.t.pods.create_volume(volume_id=mount_name)
                elif mount['type'] == 'tapissnapshot':
                    try:
                        self.t.pods.get_snapshot(snapshot_id=mount_name)
                    except:
                        raise Exception('snapshot not found')
        for template_format in template_formats:
            try:
                kwargs['pod_template'] = template_format
                results = self.t.pods.create_pod(**kwargs)
                break
            except TapisErrors.BadRequestError as e:
                if template_format != template_formats[-1]:
                    continue
                raise ValueError(f"Failed to execute pod creation due to {str(e)}")
        return results
    

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
    optional_arguments=[
        Argument('volume_mounts', arg_type='input_dict', data_type=argument.Form(
            'volume_mount', required_arguments = [
                Argument('type', choices=['tapisvolume', 'tapissnapshot', 'pvc']),
                Argument("mount_path", description='This is top level path you want to mount the volume on inside the pod. This is something like <neo4j-home>\data for a neo4j pod. Data from that path will load to the mount and become persistent')
            ],
            optional_arguments = [
                Argument('sub_path', description='If you want to only load a single file, like file.txt (which is inside the parent mount path) you can specify here')
            ]
        ), description="Used to attach the pod to an existing kubernetes volume to provide pod persistence (in case of crash). Each key is the volume_id"),
        Argument('description', arg_type='str_input', size_limit=(0, 2048)),
        Argument('command', arg_type='input_list', data_type=argument.Argument('command', arg_type='str_input'), description="Command to run in the pod"),
        Argument('environment_variables', arg_type='input_dict', data_type=argument.Argument('environment_variable', arg_type='str_input')),
        Argument('roles_required', arg_type='input_list', data_type=argument.Argument('required_role', arg_type='str_input'), description='what role is required by the user to access this pod?'),
        Argument('time_to_stop_default', data_type='int'),
        Argument('time_to_stop_instance', data_type='int'),
        Argument('networking', arg_type='input_dict', data_type=argument.Form(
            'network', required_arguments = [
                Argument('protocol', default_value='http', description='Something like https'),
                Argument('port', data_type='int', default_value=5000),
                Argument('url')
            ]
        ), description='Important networking configuration. You probably shouldnt touch this, but I wont stop you'),
        argument.Form(
            'resources', required_arguments = [
                Argument('cpu_request', data_type='int', default_value=250),
                Argument('cpu_limit', data_type='int', default_value=2000),
                Argument('mem_request', data_type='int', default_value=256),
                Argument('mem_limit', data_type='int', default_value=3072),
            ]
        )
    ]
    async def run(self, *args, **kwargs):
        pprint.pprint(kwargs)
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
    required_arguments=[
        Argument('pod_id', positional=True),
        Argument('confirm', arg_type='confirmation')
    ]
    async def run(self, *args, **kwargs) -> str:
        return_information = self.t.pods.restart_pod(pod_id=kwargs['pod_id'])
        return return_information


class stop_pod(baseCommand.BaseCommand):
    """
    @help: stop a pod's operations
    """
    return_fields = ['pod_id', 'pod_template', 'status']
    required_arguments=[
        Argument('pod_id', positional=True),
        Argument('confirm', arg_type='confirmation')
    ]
    async def run(self, *args, **kwargs):
        return_information = self.t.pods.stop_pod(pod_id=kwargs['pod_id'])
        return str(return_information)


class delete_pod(baseCommand.BaseCommand):
    """
    @help: delete select pod
    """
    required_arguments=[
        Argument('pod_id', positional=True),
        Argument('confirm', arg_type='confirmation')
    ]
    async def run(self, *args, **kwargs) -> str: 
        return_information = self.t.pods.delete_pod(pod_id=kwargs['pod_id'])
        return return_information
    

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
    required_arguments=[
        Argument('pod_id', positional=True),
        Argument('username')
    ]
    async def run(self, *args, **kwargs) -> str: # take away someones perms if they are being malicious, or something
        return_information = self.t.pods.delete_pod_permission(pod_id=kwargs['pod_id'], user=kwargs['username'])
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


class get_pod_credentials(baseCommand.BaseCommand):
    """
    @help: copy the pod password to the clipboard
    """
    required_arguments=[
        Argument('pod_id', positional=True),
    ]
    async def run(self, *args, **kwargs) -> str: # copies the pod password to clipboard so that the user can access the pod via the neo4j desktop app. Maybe a security risk? not as bad as printing passwords out!
        creds = self.t.pods.get_pod_credentials(pod_id=kwargs['pod_id'])
        username = creds.user_username
        password = creds.user_password
        pyperclip.copy(password)
        password = None
        return f'Username: {username}\nCopied password to clipboard'
    

class get_pod_uri(baseCommand.BaseCommand):
    """
    @help: get the URI for a pod
    """
    required_arguments = [
        Argument('pod_id', positional=True)
    ]
    async def run(self, *args, **kwargs):
        pod_template = self.t.pods.get_pod(pod_id=kwargs["pod_id"]).pod_template
        if pod_template == 'template/neo4j':
            return f"bolt+ssc://{kwargs['pod_id']}.pods.{self.t.base_url.split('https://')[1]}:443"
        else:
            return f"{kwargs['pod_id']}.pods.{self.t.base_url.split('https://')[1]}"


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
    

