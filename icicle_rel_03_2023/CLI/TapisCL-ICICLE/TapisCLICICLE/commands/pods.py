import pyperclip
try:
    from ..utilities import decorators
    from . import baseWrappers
except:
    import utilities.decorators as decorators
    import baseWrappers


class Pods(baseWrappers.tapisObject):
    """
    @help: Access Tapis pods through the connected service
    """
    def __init__(self, tapis_instance, username, password, connection=None):
        command_map = {
                'get_pods':self.get_pods,
                'create_pod':self.create_pod,
                'start_pod':self.start_pod,
                'restart_pod':self.restart_pod,
                'delete_pod':self.delete_pod,
                'set_pod_perms':self.set_pod_perms,
                'stop_pod':self.stop_pod,
                'delete_pod_perms':self.delete_pod_perms,
                'get_perms':self.get_perms,
                'copy_pod_password':self.copy_pod_password,
                'get_logs':self.get_pod_logs,
                'help':self.help
            }
        super().__init__(tapis_instance, username, password, connection=connection, command_map=command_map)

    def return_formatter(self, info):
        return f"Pod ID: {info.pod_id}\nPod Template: {info.pod_template}\nStatus: {info.status_requested}\n\n"

    def get_pods(self, verbose: bool, connection=None) -> str: 
        """
        @help: return a list of pods the current tapis instance has access to
        """
        pods_list = self.t.pods.get_pods()
        if verbose:
            return str(pods_list)
        pods_list = [self.return_formatter(pod) for pod in pods_list]
        pods_string = ""
        for pod in pods_list:
            pods_string += str(pod)
        return pods_string
    
    def whoami(self, verbose: bool, connection=None) -> str:
        """
        @help: returns the username of the current user
        """
        user_info = self.t.authenticator.get_userinfo()
        if verbose:
            return str(user_info)
        return user_info.username

    @decorators.RequiresForm
    def create_pod(self, id: str, template: str, verbose: bool, description: str | None = None, connection=None) -> str:
        """
        @help: create a new pod on the selected Tapis service
        """
        pod_information = self.t.pods.create_pod(pod_id=id, pod_template=template, description=description)
        if verbose:
            return str(pod_information)
        return pod_information
    
    def start_pod(self, id: str, connection=None):
        """
        @help: start the pod specified with ID
        """
        return_information = self.t.pods.start_pod(pod_id=id)
        return str(return_information)

    @decorators.NeedsConfirmation
    def restart_pod(self, id: str, verbose: bool, connection=None) -> str:
        """
        @help: initiate a pod restart
        """
        return_information = self.t.pods.restart_pod(pod_id=id)
        if verbose:
            return str(return_information)
        return return_information
    
    @decorators.NeedsConfirmation
    def stop_pod(self, id: str, connection=None):
        """
        @help: stop a pod's operations
        """
        return_information = self.t.pods.stop_pod(pod_id=id)
        return return_information
        
    @decorators.NeedsConfirmation
    def delete_pod(self, id: str, verbose: bool, connection=None) -> str: 
        """
        @help: delete select pod
        """
        return_information = self.t.pods.delete_pod(pod_id=id)
        if verbose:
            return str(return_information)
        return return_information

    def set_pod_perms(self, id: str, username: str, level: str, connection=None) -> str: # set pod permissions, given a pod id, user, and permission level
        """
        @help: set the permissions for the pod selected
        """
        return_information = self.t.pods.set_pod_permission(pod_id=id, user=username, level=level)
        return str(return_information)
    
    @decorators.NeedsConfirmation
    def delete_pod_perms(self, id: str, username: str, connection=None) -> str: # take away someones perms if they are being malicious, or something
        """
        @help: delete the selected pod from the pods service you are connected to
        """
        return_information = self.t.pods.delete_pod_perms(pod_id=id, user=username)
        return str(return_information)

    def get_perms(self, id: str, connection=None) -> str: # return a list of permissions on a given pod
        """
        @help: get the permissions list for the selected pod
        """
        return_information = self.t.pods.get_pod_permissions(pod_id=id)
        return str(return_information)

    @decorators.Auth
    def copy_pod_password(self, id: str, connection=None) -> str: # copies the pod password to clipboard so that the user can access the pod via the neo4j desktop app. Maybe a security risk? not as bad as printing passwords out!
        """
        @help: copy the pod password to the clipboard
        """
        password = self.t.pods.get_pod_credentials(pod_id=id).user_password
        pyperclip.copy(password)
        password = None
        return 'copied to clipboard'
    
    def get_pod_logs(self, id: str, file=None, connection=None):
        """
        @help: retrieve the logs of an active pod and either print them to the console, or write them to the specified file
        """
        logs = self.t.pods.get_pod_logs(pod_id=id)
        if file:
            with open(file, 'w') as f:
                f.write(logs)
            return f"Log saved at {file}"
        return logs