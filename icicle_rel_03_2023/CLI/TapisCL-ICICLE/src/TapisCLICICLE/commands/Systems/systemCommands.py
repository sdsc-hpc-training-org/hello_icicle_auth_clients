"""
Requirements:
Add a way to set a default system to be accessed. You must be able to override this by explicitly specifying system id in command
add intuitive file access and manipulation using this default system. 
"""


import json
import os
import pprint
import webbrowser


if __name__ != "__main__":
    from .. import baseCommand, decorators
    from ..arguments import argument
    from .. import commandOpts
    from socketopts import schemas
    from . import systemForms
    Argument = argument.Argument


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
base_config_path = os.path.join(__location__, '..\\..\\..\\tapis-config-files\\system-config.json')


class system(baseCommand.BaseCommand):
    """
    @help: set the system to run operations on by default. Running this will put you "in" the system so that you dont have to specify system ID for each command
    """
    required_arguments=[
        Argument('systemId', size_limit=(1, 80), positional=True),
    ]
    async def run(self, *args, **kwargs):
        system_info = self.t.systems.getSystem(systemId=kwargs['systemId'])
        kwargs['connection'].system = kwargs['systemId']
        kwargs['connection'].pwd = system_info.rootDir
        return f"successfully entered the system {kwargs['connection'].system}"


class exit_system(baseCommand.BaseCommand):
    """
    @help: exit the default system
    """
    async def run(self, *args, **kwargs):
        kwargs['connection'].system = ''
        kwargs['connection'].pwd = ''
        return "successfully exited system"
    

class get_systems(baseCommand.BaseCommand):
    """
    @help: Gets and returns the list of systems the current Tapis service and account have access to
    @doc: this is an example of the doc segment of the docstring. not included in help message
    """
    return_fields = ['id', 'systemType', 'host']
    optional_arguments = [
        Argument('listType', choices=['OWNED', 'SHARED_PUBLIC', 'ALL'])
    ]
    async def run(self, *args, **kwargs):
        systems = self.t.systems.getSystems(**kwargs)
        return systems
    

class get_system(baseCommand.BaseCommand):
    """
    @help: get information on a selected system
    """
    return_fields = ['id', 'systemType', 'host', 'enabled']
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments=[
        Argument('systemId', size_limit=(1, 80), positional=True)
    ]
    async def run(self, *args, **kwargs): 
        system_info = self.t.systems.getSystem(systemId=kwargs['systemId'])
        return system_info
    

class verify_pki_keys(baseCommand.BaseCommand):
    """
    @help: upload system credentials to a system. Must generate keys first using 'ssh-keygen -m PEM -f id_rsa', and format with, 'awk -v ORS='\\n' '1' <private_key_name>
    file argument must contain the path to the private and public keys respectively, separated by a ','
    """
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('systemId', positional=True),
        Argument('private_key_path'),
        Argument('public_key_path')
    ]
    async def run(self, *args, **kwargs): # get information about a system given its ID
        with open(kwargs['private_key_path'], 'r') as f:
            private_key = f.read()

        with open(kwargs['public_key_path'], 'r') as f:
            public_key = f.read()

        cred_return_value = self.t.systems.createUserCredential(systemId=kwargs['systemId'],
                            userName=self.username,
                            privateKey=private_key,
                            publicKey=public_key)

        return str(cred_return_value)
    

class get_scheduler_profiles(baseCommand.BaseCommand):
    """
    @help: get list of scheduler profiles in order to use while creating system
    """
    async def run(self, *args, **kwargs):
        return [{"name":scheduler.name, "description":scheduler.description, "tenant":scheduler.tenant} for scheduler in self.t.systems.getSchedulerProfiles()]
    

class SystemAuth:
    sys_auth_map = None
    def config_auth_map(self):
        self.sys_auth_map = {"LINUX":{"PASSWORD":self.password_auth, "PKI_KEYS":self.pki_keys_auth}, 
                             "S3":{"ACCESS_KEY":self.access_key_auth}, "GLOBUS":{"TOKEN":self.token_auth}, 
                             "IRODS":{"TOKEN":self.password_auth}}
        
    async def password_auth(self, **kwargs):
        request = schemas.FormRequest(request_content={'username':Argument('username', arg_type='str_input'), "password":Argument('password', arg_type='secure')},
                                        message={'message':f"Enter your credentials to the select host specified in the system creation"})
        await kwargs['connection'].send(request)
        response = await kwargs['connection'].receive()
        response_content = response.request_content
        password = response_content['password']
        loginUserName = response_content['username']
        cred_return_value = self.t.systems.createUserCredential(systemId=kwargs['id'],
                            userName=self.username,
                            loginUser=loginUserName,
                            password=password)
        return cred_return_value
    
    async def token_auth(self, **kwargs):
        session_details = self.systems.getGlobusAuthUrl()
        request = schemas.FormRequest(message={"message":f"travel to the url {session_details.url} if the page doesnt open on its own, and enter your credentials. Then paste the code displayed to this app"},
                                      request_content={'Auth_code':Argument('code', arg_type='str_input')})
        webbrowser.open(session_details.url)
        await kwargs['connection'].send(request)
        response = await kwargs['connection'].receive()
        auth_code = response.request_content['Auth_code']
        token_info = self.t.systems.generateGlobusTokens(systemId=kwargs['id'], userName=self.username, authCode=auth_code, sessionId=session_details.sessionId)
        cred_return_value = self.t.systems.createUserCredential(systemId=kwargs['id'],
                                                                userName=self.username,
                            accessToken=token_info.access_token,
                            refreshToken=token_info.refresh_token)
        return cred_return_value
    
    async def access_key_auth(self, **kwargs):
        request = schemas.FormRequest(message={"message":f"Retrieve the access key and access secret from your S3 bucket"},
                                      request_content={'access_key':Argument('access_key', arg_type='str_input'), 'access_secret':Argument('access_secret', arg_type='secure')})
        await kwargs['connection'].send(request)
        response = await kwargs['connection'].receive()
        cred_return_value = self.t.systems.createUserCredential(systemId=kwargs['id'],
                                                                userName=self.username,
                            accessKey=response.request_content['access_key'],
                            password=response.request_content['access_secret'])
        return cred_return_value
    
    async def pki_keys_auth(self, **kwargs):
        request = schemas.FormRequest(message= {"message":
                                      f"""Follow these steps to manually register PKI keys with the system
                                      1. ssh into the host you are creating your system on, {kwargs['host']}
                                      2. navigate into the .ssh folder of the host. If there are not pre-generated keys, run ssh-keygen -t rsa -b 4096 -m PEM
                                      3. format both key files using cat $privateKeyFile | awk -v ORS='\\n' '1'. Both keys must be in single line format
                                      4. ensure the private key is not in openSSH format (that is it has the begin and end headers)
                                      5. download both to your local machine using scp
                                      6. run the verify_pki_keys command and submit the system id {kwargs['id']} and the file path of the public and private keys
                                      7. you should be able to access the system now"""},
                                      request_content={"continue":Argument("continue", arg_type='confirmation')})
        await kwargs['connection'].send(request)
        await kwargs['connection'].receive()
        return None        
    
    async def base_system_auth(self, kwargs):
        if kwargs['defaultAuthnMethod'] not in self.sys_auth_map[kwargs['systemType']]:
            raise ValueError(f"The system type {kwargs['systemType']} does not support {kwargs['defaultAuthnMethod']} authentication.")
        else:
            try:
                auth_result = await self.sys_auth_map[kwargs['systemType']][kwargs['defaultAuthnMethod']](**kwargs)
                return auth_result
            except Exception as e:
                raise Exception(f"System creation for {kwargs['id']} succeeded, but Authentication for the system failed, maybe you entered something wrong? run the submit_system_credentials command")
    
    async def authenticate(self, kwargs):
        return await self.sys_auth_map[kwargs['systemType']][kwargs['defaultAuthnMethod']](**kwargs)


class create_system(baseCommand.BaseCommand, SystemAuth):
    """
    @help: create a system. Must have a properly configured system file.
    see the template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/system-config.json
    this command will automatically create and upload the ssh keys
    """
    supports_config_file=True
    required_arguments=[
        Argument('id', size_limit=(1, 80), positional=True),
        Argument('systemType', choices=["LINUX", "S3", "IRODS", "GLOBUS"], description=
                                    """LINUX is a standard linux system
IRODS refers to an IRODS data management system
GLOBUS refers to a GLOBUS file system"""),
        Argument('host', size_limit=(1, 256), description="In the case of Linux this is the hostname or IP of the HPC system you want to connect to. In the case of Globus, this is a Globus ID"),
        Argument('defaultAuthnMethod', choices=['PASSWORD', "PKI_KEYS", "TOKEN"], description=
                                    """Depending on your systemType, you will be restricted to certain options.
LINUX: PASSWORD, PKI_KEYS
GLOBUS: TOKEN
IRODS: PASSWORD
In the case you choose password, your username and password will either be your TACC account info, or the login info you used with federated/device_code grant"""),
    ]
    optional_arguments=[
        systemForms.CAN_EXEC,
        systemForms.USE_PROXY,
        systemForms.CAN_RUN_BATCH,
        systemForms.MOUNT_DATA_TRANSFER_NODE,
        systemForms.CONFIGURE_DEFAULT_JOB_CHARACTERISTICS,
        Argument('effectiveUserId', default_value=r"${apiUserId}", size_limit=(0, 60)),
        Argument('owner', default_value=r"${apiUserId}"),
        Argument('description', arg_type='str_input', size_limit=(0, 2048)),
        Argument('enabled', action='store_true'),
        Argument('rootDir', default_value='/', size_limit=(0, 4096)),
        Argument('port', data_type='int', default_value=22),
        Argument('isDtn', action='store_true', depends_on=['rootDir'], mutually_exclusive_with=['mountDataTransferNode', 'canExec']),
        Argument('enableCmdPrefix', action='store_true'),
        Argument('mpiCmd', size_limit=(0, 126), arg_type='str_input'),
        Argument('tags', arg_type='input_list', data_type=Argument('tag', arg_type='str_input')),
        Argument('notes', arg_type='str_input'),
        Argument('importRefId')
    ]
    def __init__(self):
        super().__init__()
        self.config_auth_map()

    async def run(self, *args, **kwargs) -> str: # create a tapius system. Takes a path to a json file with all system information, as well as an ID
        return_info = dict()
        return_info['system_creation_info'] = self.t.systems.createSystem(**kwargs)
        return_info['auth_result'] = await self.base_system_auth(kwargs)
        return return_info
    

class create_s3_system(create_system):
    """
    @help: create a system specially configured to support AWS s3 buckets
    """
    required_arguments = [
        Argument('id', size_limit=(1, 80), positional=True),
        Argument('host', size_limit=(1, 256), description="AWS S3 bucket url"),
        Argument('bucketName')
    ]
    optional_arguments = [
        systemForms.USE_PROXY,
        systemForms.CAN_RUN_BATCH,
        systemForms.MOUNT_DATA_TRANSFER_NODE,
        Argument('effectiveUserId', default_value=r"${apiUserId}", size_limit=(0, 60)),
        Argument('owner', default_value=r"${apiUserId}"),
        Argument('description', arg_type='str_input', size_limit=(0, 2048)),
        Argument('enabled', action='store_true'),
        Argument('rootDir', default_value='/', size_limit=(0, 4096)),
        Argument('port', data_type='int', default_value=22),
        Argument('enableCmdPrefix', action='store_true'),
        Argument('mpiCmd', size_limit=(0, 126), arg_type='str_input'),
        Argument('tags', arg_type='input_list', data_type=Argument('tag', arg_type='str_input')),
        Argument('notes', arg_type='str_input'),
        Argument('importRefId')
    ]
    async def run(self, *args, **kwargs):
        kwargs['defaultAuthnMethod'] = 'ACCESS_KEY'
        kwargs['systemType'] = 'S3', 
        return_info = dict()
        return_info['system_creation_info'] = self.t.systems.createSystem(**kwargs)
        return_info['auth_result'] = await self.base_system_auth(kwargs)
        return return_info


class submit_system_credentials(create_system):
    """
    @help: manually submit system credentials
    """
    supports_config_file = False
    required_arguments = [
        Argument('id', positional=True)
    ]
    optional_arguments = []
    async def run(self, *args, **kwargs):
        system_info = self.t.systems.getSystem(systemId=kwargs['id'])
        kwargs['systemType'] = system_info.systemType
        kwargs['defaultAuthnMethod'] = system_info.defaultAuthnMethod
        kwargs['host'] = system_info.host
        return_info = await self.authenticate(kwargs)
        return return_info
    

class SystemUpdatingRetriever(baseCommand.UpdatableFormRetriever):
    def __call__(self, tapis_instance, **kwargs):
        system_data = tapis_instance.systems.getSystem(systemId=kwargs["systemId"])
        return system_data
    

class update_system(baseCommand.BaseCommand):
    """
    @help: update a system with new information
    """
    updateable_form_retriever = SystemUpdatingRetriever()
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments=[
        Argument('systemId', size_limit=(1, 80), positional=True),
    ]
    optional_arguments=[
        systemForms.USE_PROXY,
        systemForms.CAN_RUN_BATCH,
        systemForms.MOUNT_DATA_TRANSFER_NODE,
        systemForms.CONFIGURE_DEFAULT_JOB_CHARACTERISTICS,
        Argument('defaultAuthnMethod', choices=['PASSWORD', "PKI_KEYS", "TOKEN"], description=
                                    """Depending on your systemType, you will be restricted to certain options.
LINUX: PASSWORD, PKI_KEYS
GLOBUS: TOKEN
IRODS: PASSWORD
In the case you choose password, your username and password will either be your TACC account info, or the login info you used with federated/device_code grant"""),
        Argument('jobRuntimes', arg_type='input_list', data_type=argument.Form(
            'jobRuntime', arguments_list = [
                Argument('runtimeType', choices=['DOCKER', 'SINGULARITY']), 
                Argument('version')
                ]
            )),
        Argument('jobWorkingDir', default_value=r"HOST_EVAL($WORK2)", size_limit=(0, 4096), description='Where on this hpc system are jobs run?'),
        Argument('effectiveUserId', default_value=r"${apiUserId}", size_limit=(0, 60)),
        Argument('description', arg_type='str_input', size_limit=(0, 2048)),
        Argument('port', data_type='int', default_value=22),
        Argument('enableCmdPrefix', action='store_true'),
        Argument('mpiCmd', size_limit=(0, 126), arg_type='str_input'),
        Argument('tags', arg_type='input_list', data_type=Argument('tag', arg_type='str_input')),
        Argument('notes', arg_type='str_input'),
        Argument('importRefId')
    ]
    async def run(self, *args, **kwargs):
        pprint.pprint(kwargs)
        result = self.t.systems.patchSystem(**kwargs)
        return result
    

class update_s3_system(update_system):
    """
    @help: update an s3 system
    """
    optional_arguments = [
        systemForms.USE_PROXY,
        systemForms.CAN_RUN_BATCH,
        systemForms.MOUNT_DATA_TRANSFER_NODE,
        Argument('effectiveUserId', default_value=r"${apiUserId}", size_limit=(0, 60)),
        Argument('description', arg_type='str_input', size_limit=(0, 2048)),
        Argument('port', data_type='int', default_value=22),
        Argument('enableCmdPrefix', action='store_true'),
        Argument('mpiCmd', size_limit=(0, 126), arg_type='str_input'),
        Argument('tags', arg_type='input_list', data_type=Argument('tag', arg_type='str_input')),
        Argument('notes', arg_type='str_input'),
        Argument('importRefId')
    ]
    async def run(self, *args, **kwargs):
        result = self.t.systems.patchSystem(**kwargs)
        return result


class is_system_enabled(baseCommand.BaseCommand):
    """
    @help: check to see if a system is enabled
    """
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('systemId', positional=True)
    ]
    async def run(self, *args, **kwargs):
        return self.t.systems.isEnabled(**kwargs)


class enable_system(is_system_enabled):
    """
    @help: enable a system
    """
    async def run(self, *args, **kwargs):
        return self.t.systems.enableSystem(**kwargs)
    

class disable_system(is_system_enabled):
    """
    @help: disable a system
    """
    async def run(self, *args, **kwargs):
        return self.t.systems.disableSystem(**kwargs)
    

class delete_system(baseCommand.BaseCommand):
    """
    @help: delete the selected system
    """
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments=[
        Argument('systemId', size_limit=(1, 80), positional=True),
    ]
    async def run(self, *args, **kwargs) -> str:
        kwargs['connection'].system = ''
        kwargs['connection'].pwd = ''
        return_value = self.t.systems.deleteSystem(systemId=kwargs['systemId'])
        return return_value
    

class undelete_system(baseCommand.BaseCommand):
    """
    @help: undo deletion
    """
    required_arguments=[
        Argument('systemId', size_limit=(1, 80), positional=True),
    ]
    async def run(self, *args, **kwargs):
        return self.t.systems.undeleteSystem(**kwargs)

class create_child_system(baseCommand.BaseCommand):
    """
    @help: create a child system which inherits majority attributes from parent
    """
    required_arguments = [
        Argument('parentId', positional=True),
        Argument('rootDir')
    ]
    optional_arguments = [
        Argument('effectiveUserId', default_value=r"${apiUserId}")
    ]
    async def run(self, *args, **kwargs):
        return self.t.systems.createChildSystem(**kwargs)
    

class unlink_child_system(baseCommand.BaseCommand):
    """
    @help: make a child system stand alone, so that updates to parent system will not transfer to this child system
    """
    required_arguments = [
        Argument('parentId', positional=True)
    ]
    async def run(self, *args, **kwargs):
        return self.t.systems.unlinkFromParent(**kwargs)
    

class unlink_children(baseCommand.BaseCommand):
    """
    @help: unlink an array of child systems from their parent system. Requires parent system permissions
    """
    required_arguments = [
        Argument('parentId', positional=True),
        Argument('childSystemIds', arg_type='input_list', data_type=Argument('systemId', size_limit=(1, 80)))
    ]
    async def run(self, *args, **kwargs):
        parent_id = kwargs.pop('parentId')
        kwargs['parentSystemId'] = parent_id
        return self.t.systems.unlinkChildren(**kwargs)
    

class get_user_perms(baseCommand.BaseCommand):
    """
    @help: list perms for the user on a select system
    """
    required_arguments = [
        Argument('systemId'),
        Argument('userName')
    ]
    async def run(self, *args, **kwargs):
        return self.t.systems.getUserPerms(**kwargs)
    

class grant_user_perms(baseCommand.BaseCommand):
    """
    @help: assign a perm for a user on the select system
    """
    required_arguments = [
        Argument('systemId'),
        Argument('userName'),
        Argument('permissions', arg_type='input_list', data_type=Argument('permission', choices=['READ', 'MODIFY', 'EXECUTE'], arg_type='str_input'))
    ]
    async def run(self, *args, **kwargs):
        return self.t.grantUserPerms(**kwargs)
    

class revoke_user_perms(grant_user_perms):
    """
    @help: delete user permissions
    """
    async def run(self, *args, **kwargs):
        return self.t.revokeUserPerms(**kwargs)
    

