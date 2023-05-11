from tapipy import tapis
try:
    from . import command
    from ..utilities import decorators
except:
    import command
    import utilities.decorators as decorators


class get_pods(command.BaseCommand):
    """
    @help: return a list of pods the current tapis instance has access to
    """
    async def run(self, pod_id: str=None verbose: bool=False, **kwargs) -> str: 
        pods_list = self.t.pods.get_pods()
        if verbose:
            return str(pods_list)
        pods_list = [self.return_formatter(pod) for pod in pods_list]
        pods_string = ""
        
        for pod in pods_list:
            pods_string += str(pod)
        return pods_string
    

class create_pod(command.BaseCommand):
    """
    @help: create a new pod on the selected Tapis service
    """
    decorator = decorators.RequiresForm
    async def run(self, id: str, template: str, verbose: bool, description: str | None = None, connection=None) -> str:
        pod_information = self.t.pods.create_pod(pod_id=id, pod_template=template, description=description)
        if verbose:
            return str(pod_information)
        return pod_information
    

class start_pod(command.BaseCommand):
    decorator=decorators.NeedsConfirmation
    """
    @help: start the pod specified with ID
    """


class restart_pod(command.BaseCommand):
    decorator=decorators.NeedsConfirmation
    """
    @help: initiate a pod restart
    """


class stop_pod(command.BaseCommand):
    decorator=decorators.NeedsConfirmation
    """
    @help: stop a pod's operations
    """


class delete_pod(command.BaseCommand):
    decorator=decorators.NeedsConfirmation
    """
    @help: delete select pod
    """


class set_pod_perms(command.BaseCommand):
    """
    @help: set the permissions for the pod selected
    """


class delete_pod_perms(command.BaseCommand):
    decorator=decorators.NeedsConfirmation
    """
    @help: delete the selected pod from the pods service you are connected to
    """


class get_perms(command.BaseCommand):
    """
    @help: get the permissions list for the selected pod
    """


class copy_pod_password(command.BaseCommand):
    decorator=decorators.Auth
    """
    @help: copy the pod password to the clipboard
    """


class get_pod_logs(commands.BaseCommand):
    """
    @help: retrieve the logs of an active pod and either print them to the console, or write them to the specified file
    """
        

command_ = get_pods("silly")
command_()