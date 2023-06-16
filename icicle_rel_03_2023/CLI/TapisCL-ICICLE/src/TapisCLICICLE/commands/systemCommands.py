"""
Requirements:
Add a way to set a default system to be accessed. You must be able to override this by explicitly specifying system id in command
add intuitive file access and manipulation using this default system. 
"""


import json
import os


if __name__ != "__main__":
    from . import baseCommand, decorators
    from .arguments import argument
    Argument = argument.Argument


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
base_config_path = os.path.join(__location__, '..\\..\\..\\tapis-config-files\\system-config.json')


class SystemAuth:
    auth_methods = {
        "password":"PASSWORD",
        "federated":"TOKEN",
        "device_code":"TOKEN",
        "default":"PKI_KEYS"
    }

    def password_auth(self, id):
        cred_return_value = self.t.systems.createUserCredential(systemId=id,
                            userName=self.username,
                            password=self.password)
        return cred_return_value
    
    def token_auth(self, id):
        cred_return_value = self.t.systems.createUserCredential(systemId=id,
                            access_token=self.t.access_token.access_token,
                            refresh_token=self.t.refresh_token.refresh_token)
        return cred_return_value
    
    def create_system(self, system, kwargs):
        return_value = self.t.systems.createSystem(**system)

        kwargs['connection'].pwd = system['rootDir']
        kwargs['connection'].system = system['systemId']
    
        try:
            if self.server.auth_type == "password":
                self.password_auth(system['systemId'])
            else:
                self.token_auth()
        except:
            self.t.systems.deleteSystem(systemId=system['systemId'])
            raise Exception("Authentication of system failed, cancelling system creation!")
        return return_value
    

class get_systems(baseCommand.BaseCommand):
    """
    @help: Gets and returns the list of systems the current Tapis service and account have access to
    @doc: this is an example of the doc segment of the docstring. not included in help message
    """
    async def run(self, *args, **kwargs):
        systems = self.t.systems.getSystems()
        return systems
    

class get_system_info(baseCommand.BaseCommand):
    """
    @help: get information on a selected system
    """
    required_arguments=[
        Argument('systemId', size_limit=(1, 80))
    ]
    async def run(self, *args, **kwargs): 
        system_info = self.t.systems.getSystem(systemId=kwargs['systemId'])
        return system_info
    

# class set_system_credentials(baseCommand.BaseCommand):
#     """
#     @help: upload system credentials to a system. Must generate keys first using 'ssh-keygen -m PEM -f id_rsa', and format with, 'awk -v ORS='\\n' '1' <private_key_name>
#     file argument must contain the path to the private and public keys respectively, separated by a ','
#     """
#     async def run(self, id: str, file: str, *args, **kwargs): # get information about a system given its ID
#         with open(file.split(",")[0], 'r') as f:
#             private_key = f.read()

#         with open(file.split(",")[1], 'r') as f:
#             public_key = f.read()

#         cred_return_value = self.t.systems.createUserCredential(systemId=id,
#                             userName=self.username,
#                             privateKey=private_key,
#                             publicKey=public_key)

#         return str(cred_return_value)
    

class get_scheduler_profiles(baseCommand.BaseCommand):
    """
    @help: get list of scheduler profiles in order to use while creating system
    """
    async def run(self, *args, **kwargs):
        return [{"name":scheduler.name, "description":scheduler.description, "tenant":scheduler.tenant} for scheduler in self.t.systems.getSchedulerProfiles()]


class get_scheduler_profiles_choices(argument.DynamicChoiceList):
    def __call__(self, tapis_instance):
        profiles_unfiltered = tapis_instance.systems.getSchedulerProfiles()
        return [profile.name for profile in profiles_unfiltered]
    

class create_system(baseCommand.BaseCommand, SystemAuth):
    """
    @help: create a system. Must have a properly configured system file.
    see the template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/system-config.json
    this command will automatically create and upload the ssh keys
    """
    supports_config_file=True
    required_arguments=[
        Argument('systemId', size_limit=(1, 80)),
        Argument('systemType', choices=["LINUX", "S3", "IRODS", "GLOBUS"]),
        Argument('host', size_limit=(1, 256)),
        Argument('defaultAuthnMethod', choices=['PASSWORD', "PKI_KEYS", "ACCESS_KEY", "TOKEN", "CERT"]),
        Argument('canExec', action='store_true')
    ]
    optional_arguments=[
        Argument('description', arg_type='str_input', size_limit=(0, 2048)),
        Argument('owner'),
        Argument('enabled', action='store_true'),
        Argument('effectiveUserId', default_value=r"${apiUserId}", size_limit=(0, 60)),
        Argument('bucketName'),
        Argument('rootDir', default_value='/', size_limit=(0, 4096)),
        Argument('port', data_type='int'),
        Argument('useProxy', action='store_true'),
        Argument('proxyHost', size_limit=(0, 256)),
        Argument('proxyPort', data_type='int'),
        Argument('isDtn', action='store_true'),
        Argument('dtnSystemId', size_limit=(0, 80)),
        Argument('dtnMountPoint'),
        Argument('canRunBatch', action='store_true'),
        Argument('enableCmdPrefix', action='store_true'),
        Argument('mpiCmd', size_limit=(0, 126), arg_type='str_input'),
        Argument('jobRuntimes', arg_type='input_list', data_type=argument.Form(
            'jobRuntime', arguments_list = [
                Argument('runtimeType', choices=['DOCKER', 'SINGULARITY']), 
                Argument('version')
                ]
            )),
        Argument('jobWorkingDir', default_value=r"HOST_EVAL($WORK2)", size_limit=(0, 4096)),
        Argument('jobEnvVariables', arg_type='input_list', data_type=argument.Form(
            'jobEnvironmentVariable', arguments_list = [
                Argument('key'),
                Argument('value', default_value=''),
                Argument('description', size_limit=(0, 2048), arg_type='str_input')
            ]
        )),
        Argument('jobMaxJobs', data_type='int'),
        Argument('jobMaxJobsPerUser', data_type='int'),
        Argument('batchScheduler', choices=['SLURM', "CONDOR", "PBS", "SGE", "UGE", "TORQUE"]),
        Argument('batchLogicalQueues', arg_type='input_list', data_type=argument.Form(
            'batchLogicalQueue', arguments_list = [
                Argument('name', size_limit=(1, 128)),
                Argument('hpcQueueName', size_limit=(1, 128)),
                Argument('maxJobs', data_type='int'),
                Argument('maxJobsPerUser', data_type='int'),
                Argument('minNodeCount', data_type='int'),
                Argument('maxNodeCount', data_type='int'),
                Argument('minCoresPerNode', data_type='int'),
                Argument('maxCoresPerNode', data_type='int'),
                Argument('minMemoryMB', data_type='int'),
                Argument('maxMemoryMB', data_type='int'),
                Argument('minMinutes', data_type='int'),
                Argument('maxMinutes', data_type='int')
            ]
        )),
        Argument('batchDefaultLoginQueue', size_limit=(1, 128)),
        Argument('batchSchedulerProfile', choices=get_scheduler_profiles_choices()),
        Argument('jobCapabilities', arg_type='input_list', data_type=argument.Form(
            'jobCapability', arguments_list=[
                Argument('category', choices=['SCHEUDLER', 
                                              'OS', 'HARDWARE', 
                                              'SOFTWARE', 'JOB', 
                                              'CONTAINER', 'MISC', 
                                              'CUSTOM']),
                Argument('name', size_limit=(1, 128)),
                Argument('datatype', choices=['STRING', 'INTEGER', 
                                              'BOOLEAN', 'NUMBER', 
                                              'TIMESTAMP']),
                Argument('precedence', data_type='int'),
                Argument('value')
            ]
        )),
        Argument('tags', arg_type='input_list'),
        Argument('notes', arg_type='str_input'),
        Argument('importRefId')
    ]
    async def run(self, *args, **kwargs) -> str: # create a tapius system. Takes a path to a json file with all system information, as well as an ID
        return self.t.systems.createSystem(**kwargs)

    
class create_child_system(baseCommand.BaseCommand):
    """
    @help: create a child system which inherits majority attributes from parent
    """
    async def run(self, *args, **kwargs):
        return "UNFINISHED FEATURE"
    

class system(baseCommand.BaseCommand):
    """
    @help: set the system to run operations on by default. Running this will put you "in" the system so that you dont have to specify system ID for each command
    """
    required_arguments=[
        Argument('systemId', size_limit=(1, 80))
    ]
    async def run(self, *args, **kwargs):
        system_info = self.t.systems.getSystem(systemId=kwargs['systemId'])
        kwargs['connection'].system = id
        kwargs['connection'].pwd = "/"
        return f"successfully entered the system {kwargs['connection'].system}"


class exit_system(baseCommand.BaseCommand):
    """
    @help: exit the default system
    """
    async def run(self, *args, **kwargs):
        kwargs['connection'].system = ''
        kwargs['connection'].pwd = ''
        return "successfully exited system"
    

class delete_system(baseCommand.BaseCommand):
    """
    @help: delete the selected system
    """
    decorator=decorators.NeedsConfirmation()
    required_arguments=[
        Argument('systemId', size_limit=(1, 80))
    ]
    async def run(self, *args, **kwargs) -> str:
        return_value = self.t.systems.deleteSystem(systemId=kwargs['systemId'])
        return return_value
