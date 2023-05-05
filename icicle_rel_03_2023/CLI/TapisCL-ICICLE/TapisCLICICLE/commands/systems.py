import json
import os
try:
    from ..utilities import decorators
    from . import baseWrappers
except:
    import utilities.decorators as decorators
    import commands.baseWrappers as baseWrappers


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
server_path = os.path.join(__location__, '..\\server.py')



class Systems(baseWrappers.tapisObject):
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

    async def get_systems(self, verbose: bool, connection=None):
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

    async def get_system_info(self, verbose: bool, id:str, connection=None): # get information about a system given its ID
        """
        @help: get information on a selected system
        """
        system_info = self.t.systems.getSystem(systemId=id)
        if verbose:
            return str(system_info)
        return self.return_formatter(system_info)
    
    async def create_system(self, file: str, connection=None) -> str: # create a tapius system. Takes a path to a json file with all system information, as well as an ID
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
    
    async def system_credential_upload(self, id: str, file: str, connection=None) -> str: # upload key credentials for the system
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
    async def system_password_set(self, id: str, password: str, connection=None) -> str: # set the password for a system
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
    async def delete_system(self, id: str, connection=None) -> str:
        """
        @help: delete the selected system
        """
        return_value = self.t.systems.deleteSystem(systemId=id)
        return return_value