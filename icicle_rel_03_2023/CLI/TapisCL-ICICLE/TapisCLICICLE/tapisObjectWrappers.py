import json
import pyperclip
import tapipy
from tapipy.tapis import TapisResult
from py2neo import Graph
import typing
import os
import psycopg2
try:
    from . import helpers
    from . import decorators
except:
    import helpers 
    import decorators


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
server_path = os.path.join(__location__, 'server.py')


class tapisObject(helpers.OperationsHelper, decorators.DecoratorSetup, helpers.DynamicHelpUtility):
    def __init__(self, tapis_instance, username, password, connection=None, command_map=None):
        self.t = tapis_instance
        self.username = username
        self.password = password
        self.connection = connection

        self.command_map = command_map
        
        if self.command_map:
            self.help = self.help_generation()

    def __call__(self, **kwargs):
        command = self.command_map[kwargs['command']]
        kwargs = self.filter_kwargs(command, kwargs)
        result = command(**kwargs)
        if type(result) == TapisResult:
            return str(result)
        return result
    
    def help(self, name: typing.Optional[str]):
        """
        @help: get help information for the command group
        """
        if name:
            return self.help[name]
        return self.help
    

class TapisQuery(tapisObject):
    def __init__(self, tapis_object, uname, pword, connection=None):
        super().__init__(tapis_object, uname, pword, connection=connection)
        self.t = tapis_object
        self.__code__ = self.query.__code__

    def __call__(self, **kwargs):
        kwargs = self.filter_kwargs(self.query, kwargs)
        result = self.query(**kwargs)
        return result
        
    def get_credentials(self):
        uname, pword = self.t.pods.get_pod_credentials(pod_id=id).user_username, self.t.pods.get_pod_credentials(pod_id=id).user_password
        return uname, pword


class Systems(tapisObject):
    """
    @help: Access Tapis systems through the connected service
    @doc: provides a CLI interface to the Tapis Systems service
    """
    def __init__(self, tapis_instance, username, password, connection=None):
        command_map = {
            'get_systems':self.get_systems,
            'get_system_info':self.get_system_info,
            'create_system':self.create_system,
            'set_credentials':self.system_credential_upload,
            'set_password':self.system_password_set,
            'delete_system':self.delete_system,
            'help':self.help
        }
        super().__init__(tapis_instance, username, password, connection=connection, command_map=command_map)

    def return_formatter(self, info):
        return f"id: {info.id}\nhost: {info.host}\n\n"

    def __keygen(self):
        local_files = os.listdir(__location__)
        if "id_rsa" not in local_files or "id_rsa.pub" not in local_files:
            os.system(f'ssh-keygen -q -m PEM -f {__location__}\\id_rsa -N ""')
            with open(f"{__location__}\\id_rsa", 'r') as f:
                formatted_key = ""
                for line in f.readlines()[1:-1]:
                    formatted_key += line.strip()

            with open(f"{__location__}\\id_rsa", 'w') as f:
                f.write(formatted_key)

    def get_systems(self, verbose: bool):
        """
        @help: Gets and returns the list of systems the current Tapis service and account have access to
        @doc: this is an example of the doc segment of the docstring. not included in help message
        """
        systems = self.t.systems.getSystems()
        if systems and verbose:
            return str(systems)
        systems = [self.return_formatter(system) for system in systems]
        systems_string = ''
        for system in systems:
            systems_string += system
        return systems_string

    def get_system_info(self, verbose: bool, id:str): # get information about a system given its ID
        """
        @help: get information on a selected system
        """
        system_info = self.t.systems.getSystem(systemId=id)
        if verbose:
            return str(system_info)
        return self.return_formatter(system_info)
    
    def create_system(self, file: str) -> str: # create a tapius system. Takes a path to a json file with all system information, as well as an ID
        """
        @help: create a system. Must have a properly configured system file.
        see the template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/system-config.json
        this command will automatically create and upload the ssh keys
        """
        self.__keygen()
        with open(file, 'r') as f:
            system = json.loads(f.read())
        return_value = self.t.systems.createSystem(**system)
        self.system_credential_upload(id=system['id'], file=f"{__location__}\\id_rsa,{__location__}\\id_rsa.pub")
        return str(return_value)
    
    def system_credential_upload(self, id: str, file: str) -> str: # upload key credentials for the system
        """
        @help: upload system credentials to a system. Must generate keys first using 'ssh-keygen -m PEM -f id_rsa', and format with, 'awk -v ORS='\\n' '1' <private_key_name>
        file argument must contain the path to the private and public keys respectively, separated by a ','
        """
        with open(file.split(",")[0], 'r') as f:
            private_key = f.read()

        with open(file.split(",")[1], 'r') as f:
            public_key = f.read()

        cred_return_value = self.t.systems.createUserCredential(systemId=id,
                            userName=self.username,
                            privateKey=private_key,
                            publicKey=public_key)

        return str(cred_return_value)

    @decorators.SecureInput
    def system_password_set(self, id: str, password: str) -> str: # set the password for a system
        """
        @help: set a system password
        """
        try:
            password_return_value = self.t.systems.createUserCredential(systemId=id, # will put this in a getpass later
                                userName=self.username,
                                password=password)
            return str(password_return_value)
        except Exception as e:
            raise Exception(f"{e}\nTry running set_credentials if the problem persists")

    @decorators.NeedsConfirmation
    def delete_system(self, id: str) -> str:
        """
        @help: delete the selected system
        """
        return_value = self.t.systems.deleteSystem(systemId=id)
        return return_value
    

class PostgresCLI(TapisQuery):
    """
    @help: integrated CLI to interface with Postgres pods
    """
    @decorators.RequiresExpression
    def query(self, id: str, expression: str) -> str:
        uname, pword = self.get_credentials()
        with psycopg2.connect(f"postgresql://{uname}:{pword}@{id}.pods.{self.t.base_url.split('https://')[1]}:443") as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(query=expression)
                return_value = cur.fetchall()
        return str(f'[+][{id}] {return_value}')


class Neo4jCLI(TapisQuery):
    """
    @help: integrated CLI to interface with Neo4j pods
    """
    @decorators.RequiresExpression
    def query(self, id: str, expression: str) -> str: # function to submit queries to a Neo4j knowledge graph
        uname, pword = self.get_credentials()
        graph = Graph(f"bolt+ssc://{id}.pods.{self.t.base_url.split('https://')[1]}:443", auth=(uname, pword), secure=True, verify=True)

        try:
            return_value = graph.run(expression)
            print(type(return_value))
            if str(return_value) == '(No data)' and 'create' in expression.lower(): # if no data is returned (mostly if something is created) then just say 'success'
                return f'[+][{id}@pods.{self.t.base_url.split("https://")[1]}:443] Success'
            elif str(return_value) == '(No data)':
                return f'[-][{id}@pods.{self.t.base_url.split("https://")[1]}:443] KG is empty'

            print(return_value)
            print(type(return_value))
            return str(f'[+][{id}] {return_value}')
        except Exception as e:
            return str(e)


class Pods(tapisObject):
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

    def get_pods(self, verbose: bool) -> str: 
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
    
    def whoami(self, verbose: bool) -> str:
        """
        @help: returns the username of the current user
        """
        user_info = self.t.authenticator.get_userinfo()
        if verbose:
            return str(user_info)
        return user_info.username

    @decorators.RequiresForm
    def create_pod(self, id: str, template: str, verbose: bool, description: str | None = None) -> str:
        """
        @help: create a new pod on the selected Tapis service
        """
        pod_information = self.t.pods.create_pod(pod_id=id, pod_template=template, description=description)
        if verbose:
            return str(pod_information)
        return pod_information
    
    def start_pod(self, id: str):
        """
        @help: start the pod specified with ID
        """
        return_information = self.t.pods.start_pod(pod_id=id)
        return str(return_information)

    @decorators.NeedsConfirmation
    def restart_pod(self, id: str, verbose: bool) -> str:
        """
        @help: initiate a pod restart
        """
        return_information = self.t.pods.restart_pod(pod_id=id)
        if verbose:
            return str(return_information)
        return return_information
    
    @decorators.NeedsConfirmation
    def stop_pod(self, id: str):
        """
        @help: stop a pod's operations
        """
        return_information = self.t.pods.stop_pod(pod_id=id)
        return return_information
        
    @decorators.NeedsConfirmation
    def delete_pod(self, id: str, verbose: bool) -> str: 
        """
        @help: delete select pod
        """
        return_information = self.t.pods.delete_pod(pod_id=id)
        if verbose:
            return str(return_information)
        return return_information

    def set_pod_perms(self, id: str, username: str, level: str) -> str: # set pod permissions, given a pod id, user, and permission level
        """
        @help: set the permissions for the pod selected
        """
        return_information = self.t.pods.set_pod_permission(pod_id=id, user=username, level=level)
        return str(return_information)
    
    @decorators.NeedsConfirmation
    def delete_pod_perms(self, id: str, username: str) -> str: # take away someones perms if they are being malicious, or something
        """
        @help: delete the selected pod from the pods service you are connected to
        """
        return_information = self.t.pods.delete_pod_perms(pod_id=id, user=username)
        return str(return_information)

    def get_perms(self, id: str) -> str: # return a list of permissions on a given pod
        """
        @help: get the permissions list for the selected pod
        """
        return_information = self.t.pods.get_pod_permissions(pod_id=id)
        return str(return_information)

    @decorators.Auth
    def copy_pod_password(self, id: str) -> str: # copies the pod password to clipboard so that the user can access the pod via the neo4j desktop app. Maybe a security risk? not as bad as printing passwords out!
        """
        @help: copy the pod password to the clipboard
        """
        password = self.t.pods.get_pod_credentials(pod_id=id).user_password
        pyperclip.copy(password)
        password = None
        return 'copied to clipboard'
    
    def get_pod_logs(self, id: str, file=None):
        """
        @help: retrieve the logs of an active pod and either print them to the console, or write them to the specified file
        """
        logs = self.t.pods.get_pod_logs(pod_id=id)
        if file:
            with open(file, 'w') as f:
                f.write(logs)
            return f"Log saved at {file}"
        return logs


class Files(tapisObject):
    """
    @help: Access Tapis files through the connected service
    """
    def __init__(self, tapis_instance, username, password, connection=None):
        command_map = {
            'list_files':self.list_files,
            'upload':self.upload,
            'download':self.download,
            'help':self.help
        }
        super().__init__(tapis_instance, username, password, connection=connection, command_map=command_map)

    def return_formatter(self, info):
        return f"name: {info.name}\ngroup: {info.group}\npath: {info.path}\n"

    def list_files(self, verbose: bool, id: str, file: str) -> str: # lists files available on a tapis account
        """
        @help: list the files on a system 
        """
        file_list = self.t.files.listFiles(systemId=id, path=file)
        if verbose:
            return str(file_list)
        file_list = [self.return_formatter(f) for f in file_list]
        return str(file_list)

    def upload(self, file: str, id: str) -> str: # upload a file from local to remote using tapis. Takes source and destination paths
        """
        @help: upload a file to the system 
        the source and destination files must both be in the file argument, respectively, separated by a comma
        """
        source = file.split(",")[0]
        destination = file.split(",")[1]
        self.t.upload(system_id=id,
                source_file_path=source,
                dest_file_path=destination)
        return f'successfully uploaded {source} to {destination}'
            
    def download(self, file: str, id: str) -> str: # download a remote file using tapis, operates basically the same as upload
        """
        @help: download a file from the system
        the source and destination files must both be in the file argument, respectively, separated by a comma
        """
        source = file.split(",")[0]
        destination = file.split(",")[1]
        file_info = self.t.files.getContents(systemId=id,
                            path=source)

        file_info = file_info.decode('utf-8')
        with open(destination, 'w') as f:
            f.write(file_info)
        return f'successfully downloaded {source} to {destination}'


class Apps(tapisObject):
    """
    @help: Access Tapis systems through the connected service
    """
    def __init__(self, tapis_instance, username, password, connection=None):
        command_map = {
            'create_app':self.create_app,
            'get_apps':self.get_apps,
            'delete_app':self.delete_app,
            'get_app_info':self.get_app,
            'run_app':self.run_job,
            'get_app_status':self.get_job_status,
            'download_app_results':self.download_job_output,
            'help':self.help,
        }
        super().__init__(tapis_instance, username, password, connection=connection, command_map=command_map)

    def create_app(self, file: str) -> str: # create a tapis app taking a json descriptor file path
        """
        @help: create an app. You must have a properly configured app config file. 
        See a template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/app-config.json
        """
        with open(file, 'r') as f:
            app_def = json.loads(f.read())
        url = self.t.apps.createAppVersion(**app_def)
        return f"App created successfully\nID: {app_def['id']}\nVersion: {app_def['version']}\nURL: {url}\n"

    def get_apps(self) -> str:
        """
        @help: get all the apps on a system
        """
        apps = self.t.apps.getApps()
        return str(apps)

    @decorators.NeedsConfirmation
    def delete_app(self, id: str, version: str) -> str:
        """
        @help: delete the selected app
        """
        return_value = self.t.apps.deleteApp(appId=id, appVersion=version)
        return str(return_value)

    def get_app(self, verbose: bool, id: str, version: str)-> None | str: # returns app information with an id and version as arguments
        """
        @help: return selected app information
        """
        app = self.t.apps.getApp(appId=id, appVersion=version)
        if verbose:
            return str(app)
        return None

    def run_job(self, file: str)->str: # run a job using an app. Takes a job descriptor json file path
        """
        @help: run a job from an app on a system. You must have a properly configured job config file. 
        See a template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/job-config.json
        """
        with open(file, 'r') as f:
            app = json.loads(f.read())
        job = self.t.jobs.submitJob(**app)
        return str(job.uuid)

    def get_job_status(self, uuid: str)->str: # return a job status with its Uuid
        """
        @help: get the status of a job
        """
        job_status = self.t.jobs.getJobStatus(jobUuid=uuid)
        return str(job_status)

    def download_job_output(self, uuid: str, file: str)->str: # download the output of a job with its Uuid
        """
        @help: download a job output from the system 
        """
        jobs_output = self.t.jobs.getJobOutputDownload(jobUuid=uuid, outputPath='tapisjob.out')
        with open(file, 'w') as f:
            f.write(jobs_output)
        return f"Successfully downloaded job output to {file}"
    