from tapipy import tapis
import pyperclip
try:
    from . import baseCommand
    from . import decorators
except:
    import commands.baseCommand as baseCommand
    import commands.decorators as decorators


class get_pods(baseCommand.BaseCommand):
    """
    @help: return a list of pods the current tapis instance has access to
    @todo: add feature so that an individual pod id can be passed to access pod specific
    """
    async def run(self, *args, **kwargs) -> str: 
        pods_list = self.t.pods.get_pods()
        return pods_list

class create_pod(baseCommand.BaseCommand):
    """
    @help: create a new pod on the selected Tapis service
    """
    decorator = decorators.RequiresForm()
    async def run(self, id: str, template: str, 
                  description: str | None = None, *args, **kwargs) -> str:
        pod_information = self.t.pods.create_pod(pod_id=id, pod_template=template, description=description)
        return pod_information
    

class start_pod(baseCommand.BaseCommand):
    """
    @help: start the pod specified with ID
    """
    async def run(self, id: str, *args, **kwargs):
        return_information = self.t.pods.start_pod(pod_id=id)
        return return_information

class restart_pod(baseCommand.BaseCommand):
    """
    @help: initiate a pod restart
    """
    decorator=decorators.NeedsConfirmation()
    async def run(self, id: str, *args, **kwargs) -> str:
        return_information = self.t.pods.restart_pod(pod_id=id)
        return return_information


class stop_pod(baseCommand.BaseCommand):
    """
    @help: stop a pod's operations
    """
    decorator=decorators.NeedsConfirmation()
    async def run(self, id: str, *args, **kwargs):
        return_information = self.t.pods.stop_pod(pod_id=id)
        return return_information


class delete_pod(baseCommand.BaseCommand):
    """
    @help: delete select pod
    """
    decorator=decorators.NeedsConfirmation()
    async def run(self, id: str, *args, **kwargs) -> str: 
        return_information = self.t.pods.delete_pod(pod_id=id)
        return return_information
    

class set_pod_perms(baseCommand.BaseCommand):
    """
    @help: set the permissions for the pod selected
    """
    async def run(self, id: str, username: str, level: str, *args, **kwargs) -> str: # set pod permissions, given a pod id, user, and permission level
        return_information = self.t.pods.set_pod_permission(pod_id=id, user=username, level=level)
        return return_information


class delete_pod_perms(baseCommand.BaseCommand):
    """
    @help: delete the selected pod from the pods service you are connected to
    """
    decorator=decorators.NeedsConfirmation()
    async def run(self, id: str, username: str, *args, **kwargs) -> str: # take away someones perms if they are being malicious, or something
        return_information = self.t.pods.delete_pod_perms(pod_id=id, user=username)
        return return_information


class get_perms(baseCommand.BaseCommand):
    """
    @help: get the permissions list for the selected pod
    """
    async def run(self, id: str, *args, **kwargs) -> str: # return a list of permissions on a given pod
        return_information = self.t.pods.get_pod_permissions(pod_id=id)
        return return_information


class copy_pod_password(baseCommand.BaseCommand):
    """
    @help: copy the pod password to the clipboard
    """
    decorator=decorators.Auth()
    async def run(self, id: str, username=None, password=None, *args, **kwargs) -> str: # copies the pod password to clipboard so that the user can access the pod via the neo4j desktop app. Maybe a security risk? not as bad as printing passwords out!
        password = self.t.pods.get_pod_credentials(pod_id=id).user_password
        pyperclip.copy(password)
        password = None
        return 'copied to clipboard'


class get_pod_logs(baseCommand.BaseCommand):
    """
    @help: retrieve the logs of an active pod and either print them to the console, or write them to the specified file
    """
    async def run(self, id: str, file=None, *args, **kwargs):
        logs = self.t.pods.get_pod_logs(pod_id=id)
        if file:
            with open(file, 'w') as f:
                f.write(logs)
            return f"Log saved at {file}"
        return logs
    

