from tapipy import tapis
import pyperclip
import json
import os
try:
    from . import baseCommand
    from ..utilities import decorators
except:
    import commands.baseCommand as baseCommand
    import utilities.decorators as decorators


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
server_path = os.path.join(__location__, '..\\server.py')


class get_systems(baseCommand.BaseCommand):
    """
    @help: Gets and returns the list of systems the current Tapis service and account have access to
    @doc: this is an example of the doc segment of the docstring. not included in help message
    """
    async def run(self, verbose: bool, *args, **kwargs):
        systems = self.t.systems.getSystems()
        if systems and verbose:
            return str(systems)
        systems = [self.return_formatter(system) for system in systems]
        systems_string = ''
        for system in systems:
            systems_string += system
        return systems_string
    

class get_system_info(baseCommand.BaseCommand):
    """
    @help: get information on a selected system
    """
    async def run(self, verbose: bool, id:str, *args, **kwargs): 
        system_info = self.t.systems.getSystem(systemId=id)
        if verbose:
            return str(system_info)
        return self.return_formatter(system_info)
    

class create_system(baseCommand.BaseCommand):
    """
    @help: create a system. Must have a properly configured system file.
    see the template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/system-config.json
    this command will automatically create and upload the ssh keys
    """
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


    async def run(self, file: str, *args, **kwargs) -> str: # create a tapius system. Takes a path to a json file with all system information, as well as an ID
        self.__keygen()
        with open(file, 'r') as f:
            system = json.loads(f.read())
        return_value = self.t.systems.createSystem(**system)
        self.system_credential_upload(id=system['id'], file=f"{__location__}\\id_rsa,{__location__}\\id_rsa.pub")
        return str(return_value)
    

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
    

class set_system_password(baseCommand.BaseCommand):
    """
    @help: set a system password
    """
    decorator=decorators.SecureInput()
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
