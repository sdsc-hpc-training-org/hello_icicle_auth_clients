"""
Requirements:
Add a way to set a default system to be accessed. You must be able to override this by explicitly specifying system id in command
add intuitive file access and manipulation using this default system. 
"""


import json
import os


if __name__ != "__main__":
    from . import baseCommand, decorators


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
    def keygen(self):
        local_files = os.listdir(__location__)
        if "id_rsa" not in local_files or "id_rsa.pub" not in local_files:
            os.system(f'ssh-keygen -q -m PEM -f {__location__}\\id_rsa -N ""')
            with open(f"{__location__}\\id_rsa", 'r') as f:
                formatted_key = ""
                for line in f.readlines()[1:-1]:
                    formatted_key += line.strip()

            with open(f"{__location__}\\id_rsa", 'w') as f:
                f.write(formatted_key)

    def password_auth(self, id):
        cred_return_value = self.t.systems.createUserCredential(systemId=id,
                            userName=self.username,
                            password=self.password)
        return cred_return_value
    
    def create_system(self, system, kwargs):
        return_value = self.t.systems.createSystem(**system)

        kwargs['connection'].pwd = system['rootDir']
        kwargs['connection'].system = system['id']
    
        if self.server.auth_type == "password":
            self.password_auth(system['id'])
        else:
            self.keygen()
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
    async def run(self, id:str, *args, **kwargs): 
        system_info = self.t.systems.getSystem(systemId=id)
        return system_info
    

class set_system_credentials(baseCommand.BaseCommand):
    """
    @help: upload system credentials to a system. Must generate keys first using 'ssh-keygen -m PEM -f id_rsa', and format with, 'awk -v ORS='\\n' '1' <private_key_name>
    file argument must contain the path to the private and public keys respectively, separated by a ','
    """
    async def run(self, id: str, file: str, *args, **kwargs): # get information about a system given its ID
        with open(file.split(",")[0], 'r') as f:
            private_key = f.read()

        with open(file.split(",")[1], 'r') as f:
            public_key = f.read()

        cred_return_value = self.t.systems.createUserCredential(systemId=id,
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


class create_system(baseCommand.BaseCommand, SystemAuth):
    """
    @help: create a system. Must have a properly configured system file.
    see the template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/system-config.json
    this command will automatically create and upload the ssh keys
    """
    decorator = decorators.RequiresForm()
    async def run(self, id: str, description=None, systemType=['LINUX', 'S3', 'IRODS', 'GLOBUS'],
        jobRuntime=["DOCKER", "SINGULARITY"],
        batchScheduler=['SLURM', 'CONDOR', 'PBS', 'SGE', 'UGE', 'TORQUE'],
        batchSchedulerProfile=['tacc'], *args, **kwargs) -> str: # create a tapius system. Takes a path to a json file with all system information, as well as an ID
        
        system["defaultAuthnMethod"] = self.auth_methods[self.server.auth_type]
        with open(base_config_path, 'r') as f:
            system = json.loads(f.read())
            system['id'] = id
            system['description'] = description
            system['systemType'] = systemType
            system['jobRunTimes'] = [{"runtimeType":jobRuntime}]
            system['batchScheduler'] = batchScheduler
            system['batchSchedulerProfile'] = batchSchedulerProfile
        return_value = self.create_system(system, kwargs)
        return return_value
    

class create_system_from_file(baseCommand.BaseCommand, SystemAuth):
    """
    @help: create a system from a config file
    """
    async def run(self, file: str, *args, **kwargs):
        with open(file, 'r') as f:
            system = json.loads(f.read())

        return_value = self.create_system(system, kwargs)
        return return_value
    

class create_child_system(baseCommand):
    """
    @help: create a child system which inherits majority attributes from parent
    """
    async def run(self, parent_id: str, id: str):
        pass
    

class system(baseCommand.BaseCommand):
    """
    @help: set the system to run operations on by default. Running this will put you "in" the system so that you dont have to specify system ID for each command
    """
    async def run(self, id, *args, **kwargs):
        system_info = self.t.systems.getSystem(systemId=id)
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
    

class set_system_password(baseCommand.BaseCommand):
    """
    @help: set a system password
    """
    decorator=decorators.RequiresForm()
    async def run(self, id: str, password: str=None, *args, **kwargs) -> str: # set the password for a system
        try:
            password_return_value = self.t.systems.createUserCredential(systemId=id, # will put this in a getpass later
                                userName=self.username,
                                password=password)
            return str(password_return_value)
        except Exception as e:
            raise Exception(f"{e}\nTry running set_credentials if the problem persists")
        

class delete_system(baseCommand.BaseCommand):
    """
    @help: delete the selected system
    """
    decorator=decorators.NeedsConfirmation()
    async def run(self, id: str, *args, **kwargs) -> str:
        return_value = self.t.systems.deleteSystem(systemId=id)
        return return_value
