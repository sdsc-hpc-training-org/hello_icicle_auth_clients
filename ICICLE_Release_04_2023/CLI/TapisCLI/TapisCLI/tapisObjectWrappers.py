import json
import os
import re
import sys
import pyperclip
from tapipy import tapis
import tapipy
from py2neo import Graph


class tapisObject:
    def __init__(self, tapis_instance, username, password):
        self.t = tapis_instance
        self.username = username
        self.password = password

        dirname = os.path.dirname(__file__)
        root_path = re.findall(r'^(.*?\\TapisCLI)', dirname)[0]
        rel_path = r"\subsystems\help.json"
        self.help_path = f'{root_path}{rel_path}'

        with open(self.help_path, 'r') as h:
            json_help = h.read()
            self.help = json.loads(json_help)


class Systems(tapisObject):
    def return_formatter(self, info):
        return f"id: {info.id}\nhost: {info.host}\n"

    def get_system_list(self, **kwargs): # return a list of systems active on the account
        try:
            systems = self.t.systems.getSystems()
            if systems and kwargs['verbose']:
                return str(systems)
            elif systems and not kwargs['verbose']:
                systems = [self.return_formatter(system) for system in systems]
                systems_string = ''
                for system in systems:
                    systems_string += system
                return systems_string

            return "[-] No systems registered"
        except Exception as e:
            raise e

    def get_system_info(self, **kwargs): # get information about a system given its ID
        try:
            system_info = self.t.systems.getSystem(systemId=kwargs["id"])
            if kwargs['verbose']:
                return str(system_info)
            return self.return_formatter(system_info)
        except Exception as e:
            raise e
        
    def create_system(self, **kwargs): # create a tapius system. Takes a path to a json file with all system information, as well as an ID
        try:
            with open(kwargs['file'], 'r') as f:
                system = json.loads(f.read())
            system_id = system['id']
            self.t.systems.createSystem(**system)
            return str(system_id)
        except Exception as e:
            raise e

    def system_credential_upload(self, **kwargs): # upload key credentials for the system
        try:
            with open(kwargs['file'].split(",")[0], 'r') as f:
                private_key = f.read()

            with open(kwargs['file'].split(",")[1], 'r') as f:
                public_key = f.read()

            cred_return_value = self.t.systems.createUserCredential(systemId=kwargs['id'],
                                userName=self.username,
                                privateKey=private_key,
                                publicKey=public_key)

            return str(cred_return_value)
        except Exception as e:
            raise e

    def system_password_set(self, **kwargs): # set the password for a system
        try:
            password_return_value = self.t.systems.createUserCredential(systemId=kwargs['id'], # will put this in a getpass later
                                userName=self.username,
                                password=kwargs['password'])
            return str(password_return_value)
        except Exception as e:
            raise e

    def delete_system(self, **kwargs):
        try:
            return_value = self.t.systems.deleteSystem(systemId=kwargs['id'])
            return return_value
        except Exception as e:
            raise e

    def systems_cli(self, **kwargs): # function for managing all of the system commands, makes life easier later
        command = kwargs['command']
        try:
            match command:
                case 'get_systems':
                    return self.get_system_list(**kwargs)
                case 'get_system_info':
                    return self.get_system_info(**kwargs)
                case 'create_system':
                    return self.create_system(**kwargs)
                case "set_credentials":
                    return self.system_credential_upload(**kwargs)
                case "set_password":
                    return self.system_password_set(**kwargs)
                case "delete_system":
                    return self.delete_system(**kwargs)
                case "help":
                    return self.help['systems']
                case _:
                    raise Exception('Command not recognized')
        except IndexError:
            raise Exception("must specify subcommand. See 'help'")


class Neo4jCLI(tapisObject):
    def __init__(self, tapis_object, uname, pword):
        super().__init__(tapis_object, uname, pword)
        self.t = tapis_object
   
    def submit_query(self, **kwargs): # function to submit queries to a Neo4j knowledge graph
        id_ = kwargs['id']
        uname, pword = self.t.pods.get_pod_credentials(pod_id=id_).user_username, self.t.pods.get_pod_credentials(pod_id=id_).user_password
        graph = Graph(f"bolt+ssc://{id_}.pods.icicle.tapis.io:443", auth=(uname, pword), secure=True, verify=True)
        if kwargs['file']:
            with open(kwargs['file'], 'r') as f:
                expression = f.read()
        else:
            expression = kwargs['expression']
        
        try:
            return_value = graph.run(expression)
            print(type(return_value))
            if str(return_value) == '(No data)' and 'create' in expression.lower(): # if no data is returned (mostly if something is created) then just say 'success'
                return f'[+][{id_}@pods.icicle.tapis.io:443] Success'
            elif str(return_value) == '(No data)':
                return f'[-][{id_}@pods.icicle.tapis.io:443] KG is empty'

            return str(f'[+][{id_}] {return_value}')
        except Exception as e:
            return str(e)


class Pods(tapisObject):
    def return_formatter(self, info):
        return f"pod_id: {info.pod_id}\npod_template: {info.pod_template}\nurl: {info.url}\nstatus_requested: {info.status_requested}\n\n"

    def get_pods(self, **kwargs): # returns a list of pods
        pods_list = self.t.pods.get_pods()
        if kwargs['verbose']:
            return str(pods_list)
        pods_list = [self.return_formatter(pod) for pod in pods_list]
        pods_string = ""
        for pod in pods_list:
            pods_string += str(pod)
        return pods_string
        
    def whoami(self, **kwargs): # returns user information
        user_info = self.t.authenticator.get_userinfo()
        if kwargs['verbose']:
            return str(user_info)
        return user_info.username

    def create_pod(self, **kwargs): # creates a pod with a pod id, template, and description
        try:
            pod_description = kwargs['description']#str(input("Enter your pod description below:\n")) 
            pod_information = self.t.pods.create_pod(pod_id=kwargs['id'], pod_template=kwargs['template'], description=pod_description)
            if kwargs['verbose']:
                return str(pod_information)
            return self.return_formatter(pod_information)
        except Exception as e:
            raise e

    def restart_pod(self, **kwargs): # restarts a pod if needed
        try:
            return_information = self.t.pods.restart_pod(pod_id=kwargs["id"])
            if kwargs['verbose']:
                return str(return_information)
            return self.return_formatter(return_information)
        except Exception as e:
            raise e

    def delete_pod(self, **kwargs): # deletes a pod
        try:
            return_information = self.t.pods.delete_pod(pod_id=kwargs["id"])
            if kwargs['verbose']:
                return str(return_information)
            return self.return_formatter(return_information)
        except Exception as e:
            raise e

    def set_pod_perms(self, **kwargs): # set pod permissions, given a pod id, user, and permission level
        try:
            return_information = self.t.pods.set_pod_permission(pod_id=kwargs["id"], user=kwargs['username'], level=kwargs['level'])
            return str(return_information)
        except tapipy.errors.BaseTapyException:
            raise Exception('Invalid level given')
        except Exception as e:
            raise e
    
    def delete_pod_perms(self, **kwargs): # take away someones perms if they are being malicious, or something
        try:
            return_information = self.t.pods.delete_pod_perms(pod_id=kwargs["id"], user=kwargs['username'])
            return str(return_information)
        except Exception as e:
            raise e

    def get_perms(self, **kwargs): # return a list of permissions on a given pod
        try:
            return_information = self.t.pods.get_pod_permissions(pod_id=kwargs["id"])
            return str(return_information)
        except IndexError:
            raise Exception('enter valid pod id, see help')
        except Exception as e:
            raise e

    def copy_pod_password(self, **kwargs): # copies the pod password to clipboard so that the user can access the pod via the neo4j desktop app. Maybe a security risk? not as bad as printing passwords out!
        try:
            password = self.t.pods.get_pod_credentials(pod_id=kwargs["id"]).user_password
            pyperclip.copy(password)
            password = None
            return 'copied to clipboard'
        except Exception as e:
            raise e

    def pods_cli(self, **kwargs):
        command = kwargs['command']
        try:
            match command:
                case 'get_pods':
                    return self.get_pods(**kwargs)
                case 'create_pod':
                    return self.create_pod(**kwargs)
                case 'restart_pod':
                    return self.restart_pod(**kwargs)
                case 'delete_pod':
                    return self.delete_pod(**kwargs)
                case "set_pod_perms":
                    return self.set_pod_perms(**kwargs)
                case 'delete_pod_perms':
                    return self.delete_pod_perms(**kwargs)
                case 'get_perms':
                    return self.get_perms(**kwargs)
                case "copy_pod_password":
                    return self.copy_pod_password(**kwargs)
                case "help":
                    return self.help['pods']
                case _:
                    raise Exception(f'Command {command} not recognized')
        except IndexError:
            raise Exception("must specify subcommand. See 'help'")


class Files(tapisObject):
    def return_formatter(self, info):
        return f"name: {info.name}\ngroup: {info.group}\npath: {info.path}\n"

    def list_files(self, **kwargs): # lists files available on a tapis account
        try:
            file_list = self.t.files.listFiles(systemId=kwargs['id'], path=kwargs['file'])
            if kwargs['verbose']:
                return str(file_list)
            file_list = [self.return_formatter(f) for f in file_list]
        except Exception as e:
            raise e

    def upload(self, **kwargs): # upload a file from local to remote using tapis. Takes source and destination paths
        try:
            source = kwargs["file"].split(",")[0]
            destination = kwargs["file"].split(",")[1]
            self.t.upload(system_id=kwargs['id'],
                    source_file_path=source,
                    dest_file_path=destination)
            return f'successfully uploaded {source} to {destination}'
        except:
            raise Exception(f'failed to upload {source} to {destination}')
            
    def download(self, **kwargs): # download a remote file using tapis, operates basically the same as upload
        try:
            source = kwargs["file"].split(",")[0]
            destination = kwargs["file"].split(",")[1]
            file_info = self.t.files.getContents(systemId=kwargs['id'],
                                path=source)

            file_info = file_info.decode('utf-8')
            with open(destination, 'w') as f:
                f.write(file_info)
            return f'successfully downloaded {source} to {destination}'
        except:
            raise Exception(f'failed to download {source} to {destination}')

    def files_cli(self, **kwargs): # function to manage all the file commands
        command = kwargs['command']
        try:
            match command:
                case'list_files':
                    return self.list_files(**kwargs)
                case 'upload':
                    return self.upload(**kwargs)
                case 'download':
                    return self.download(**kwargs)
                case "help":
                    return self.help['files']
                case _:
                    raise Exception('Command not recognized')
        except IndexError:
            raise Exception("must specify subcommand. See 'help'")
        except Exception as e:
            raise e


class Apps(tapisObject):
    def create_app(self, **kwargs): # create a tapis app taking a json descriptor file path
        try:
            with open(kwargs['file'], 'r') as f:
                app_def = json.loads(f.read())
            url = self.t.apps.createAppVersion(**app_def)
            return f"App created successfully\nID: {app_def['id']}\nVersion: {app_def['version']}\nURL: {url}\n"
        except Exception as e:
            raise e

    def get_apps(self, **kwargs):
        try:
            apps = self.t.apps.getApps()
            return str(apps)
        except Exception as e:
            raise e

    def delete_app(self, **kwargs):
        try:
            return_value = self.t.apps.deleteApp(appId=kwargs['id'], appVersion=kwargs['version'])
            return str(return_value)
        except Exception as e:
            raise e

    def get_app(self, **kwargs): # returns app information with an id and version as arguments
        try:
            app = self.t.apps.getApp(appId=kwargs['id'], appVersion=kwargs['version'])
            if kwargs['verbose']:
                return str(app)
            return 
        except Exception as e:
            raise e

    def run_job(self, **kwargs): # run a job using an app. Takes a job descriptor json file path
        try:
            with open(kwargs['file'], 'r') as f:
                app_args = json.loads(f.read())

            job = {
                "name": kwargs['name'],
                "appId": kwargs['id'], 
                "appVersion": kwargs['version'],
                "parameterSet": {"appArgs": [app_args]        
                                }
            }
            job = self.t.jobs.submitJob(**job)
            return str(job.uuid)
        except Exception as e:
            raise e

    def get_job_status(self, **kwargs): # return a job status with its Uuid
        try:
            job_status = self.t.jobs.getJobStatus(jobUuid=kwargs['uuid'])
            return str(job_status)
        except Exception as e:
            raise e

    def download_job_output(self, **kwargs): # download the output of a job with its Uuid
        try:
            jobs_output = self.t.jobs.getJobOutputDownload(jobUuid=kwargs['uuid'], outputPath='tapisjob.out')
            with open(kwargs['file'], 'w') as f:
                f.write(jobs_output)
            return f"Successfully downloaded job output to {kwargs['file']}"
        except Exception as e:
            raise e

    def apps_cli(self, **kwargs): # function to manage all jobs
        command = kwargs['command']
        try:
            match command:
                case 'create_app':
                    return self.create_app(**kwargs)
                case 'get_apps':
                    return self.get_apps(**kwargs)
                case 'delete_app':
                    return self.delete_app(**kwargs)
                case 'get_app_info':
                    return self.get_app(**kwargs)
                case 'run_app':
                    return self.run_job(**kwargs)
                case 'get_app_status':
                    return self.get_job_status(**kwargs)
                case 'download_app_results':
                    return self.download_job_output(**kwargs)
                case "help":
                    return self.help['apps']
                case _:
                    raise Exception('Command not recognized')
        except IndexError:
            raise Exception("must specify subcommand. See 'help'")
        except Exception as e:
            raise e