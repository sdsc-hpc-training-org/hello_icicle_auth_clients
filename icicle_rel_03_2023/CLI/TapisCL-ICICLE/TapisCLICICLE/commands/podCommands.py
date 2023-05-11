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
    async def run(self, verbose: bool, **kwargs) -> str: 
        pods_list = self.t.pods.get_pods()
        if verbose:
            return str(pods_list)
        pods_list = [self.return_formatter(pod) for pod in pods_list]
        pods_string = ""
        for pod in pods_list:
            pods_string += str(pod)
        return pods_string
    

class create_pod(commands.BaseCommand):
    """
    @help: create a new pod on the selected Tapis service
    """
    decorator = decorators.
    async def run()