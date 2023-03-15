import sys
from tapipy.tapis import Tapis
import pyperclip
from py2neo import Graph

sys.path.insert(1, r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems')
from tapisobject import tapisObject


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
    def __init__(self, tapis_object, username, password):
        super().__init__(tapis_object, username, password)
        self.neo4j = Neo4jCLI(tapis_object, username, password)

    def get_pods(self): # returns a list of pods
        pods_list = self.t.pods.get_pods()
        pods_list = ''.join([repr(pod) for pod in pods_list])
        print(type(pods_list))
        print(type(pods_list[0]))
        print(pods_list)
        return pods_list
    
    def whoami(self): # returns user information
        user_info = self.t.authenticator.get_userinfo()
        return str(user_info)

    def create_pod(self, **kwargs): # creates a pod with a pod id, template, and description
        try:
            pod_description = kwargs['description']#str(input("Enter your pod description below:\n")) 
            pod_information = self.t.pods.create_pod(pod_id=kwargs['id'], pod_template=kwargs['template'], description=pod_description)
            return str(pod_information)
        except Exception as e:
            raise e

    def restart_pod(self, **kwargs): # restarts a pod if needed
        decision = input(f'Please enter, "Restart pod {kwargs["id"]}"\nNote that data may not be persistent on restart') # user confirmation
        if decision == f'Restart pod {kwargs["id"]}':
            return 'Restart Aborted'

        try:
            return_information = self.t.pods.restart_pod(pod_id=kwargs["id"])
            return return_information
        except Exception as e:
            raise e

    def delete_pod(self, **kwargs): # deletes a pod
        decision = input(f'Please enter, "Delete pod {kwargs["id"]}"\nNote that all data WILL BE LOST') # user confirmation
        if decision == f'Delete pod {kwargs["id"]}':
            return 'Deletion Aborted'

        try:
            return_information = self.t.pods.delete_pod(pod_id=kwargs["id"])
            return return_information
        except Exception as e:
            raise e

    def set_pod_perms(self, **kwargs): # set pod permissions, given a pod id, user, and permission level
        try:
            return_information = self.t.pods.set_pod_permission(pod_id=kwargs["id"], user=kwargs['username'], level=kwargs['level'])
            return return_information
        except tapipy.errors.BaseTapyException:
            raise Exception('Invalid level given')
        except Exception as e:
            raise e
    
    def delete_pod_perms(self, **kwargs): # take away someones perms if they are being malicious, or something
        try:
            return_information = self.t.pods.delete_pod_perms(pod_id=kwargs["id"], user=kwargs['username'])
            return return_information
        except Exception as e:
            raise e

    def get_perms(self, **kwargs): # return a list of permissions on a given pod
        try:
            return_information = self.t.pods.get_pod_permissions(pod_id=kwargs["id"])
            return return_information
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
            if command == 'get_pods':
                return self.get_pods()
            elif command == 'create_pod':
                return self.create_pod(**kwargs)
            elif command == 'restart_pod':
                return self.restart_pod(**kwargs)
            elif command == 'delete_pod':
                return self.delete_pod(**kwargs)
            elif command == "set_pod_perms":
                return self.set_pod_perms(**kwargs)
            elif command == 'delete_pod_perms':
                return self.delete_pod_perms(**kwargs)
            elif command == 'get_perms':
                return self.get_perms(**kwargs)
            elif command == "copy_pod_password":
                return self.copy_pod_password(**kwargs)
            elif command == 'query':
                return self.neo4j.kg_query_cli(**kwargs)
            else:
                raise Exception(f'Command {command} not recognized')
        except IndexError:
            raise Exception("must specify subcommand. See 'help'")