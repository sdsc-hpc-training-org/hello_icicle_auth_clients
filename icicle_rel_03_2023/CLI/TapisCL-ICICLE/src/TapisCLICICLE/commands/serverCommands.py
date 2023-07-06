import typing

from tapipy.tapis import Tapis


if __name__ != "__main__":
    from . import baseCommand, decorators
    from utilities import exceptions
    from commands.arguments.argument import Argument


class get_tenants(baseCommand.BaseCommand):
    """
    @help: get a list of available tenants to authenticate with
    """
    async def run(self, *args, **kwargs):
        return_data = dict()
        tenants = self.t.tenants.list_tenants()
        for tenant in tenants:
            return_data[tenant.tenant_id] = {'uri':tenant.base_url.split('//')[1], 'owner':tenant.owner, 'description':tenant.description}
        return return_data
    

class get_tenant(baseCommand.BaseCommand):
    """
    @help: get a specific tenant
    """
    required_arguments = [
        Argument('tenant_id', positional=True)
    ]
    async def run(self, *args, **kwargs):
        tenant = self.t.tenants.get_tenant(**kwargs)
        return {'uri':tenant.base_url.split('//')[1], 'owner':tenant.owner, 'description':tenant.description}
    
    
class switch_service_to(baseCommand.BaseCommand):
    """
    @help: switch the connected tapis service
    @todo: upgrade to federated auth
    """
    required_arguments=[
        Argument('tenant_uri', size_limit=(0, 80), positional=True),
        Argument('auth', choices=['password', 'device_code', 'federated']),
    ]
    async def run(self, *args, **kwargs):  # tenant_uri is the baseURL
        auth = kwargs['auth']
        tenant_uri = kwargs['tenant_uri']
        self.server.auth_type = auth
        if auth == "password":
            results = await self.server.password_grant(tenant_uri, kwargs['connection'])
        elif auth == "device_code":
            results = await self.server.device_code_grant(tenant_uri, kwargs['connection'])
        elif auth == "federated":
            results = await self.server.federated_grant(tenant_uri, kwargs['connection'])
        else:
            results = None
        self.server.configure_decorators(self.server.username, self.server.password)
        self.server.update_credentials(self.server.t, self.server.username, self.server.password)
        return results
      

class exit(baseCommand.BaseCommand):
    """
    @help: exit the CLI without shutting down the service
    """
    async def run(self, *args, **kwargs):
        raise exceptions.Exit
    

class shutdown(baseCommand.BaseCommand):
    """
    @help: exit the CLI and shutdown the service
    """
    async def run(self, *args, **kwargs):
        raise exceptions.Shutdown
    
    
class whoami(baseCommand.BaseCommand):
    """
    @help: returns the username of the current user
    """
    async def run(self, *args, **kwargs) -> str:
        user_info = self.t.authenticator.get_userinfo()
        return user_info
    

class user(baseCommand.BaseCommand):
    """
    @help: returns the username of the selected user
    """
    required_arguments = [
        Argument('username', positional=True)
    ]
    async def run(self, *args, **kwargs):
        return self.t.authenticator.get_profile(**kwargs)

class get_args(baseCommand.BaseCommand):
    """
    @help: get the list of possible arguments 
    """
    async def run(self, *args, **kwargs):
        return self.server.arguments
    

class whereami(baseCommand.BaseCommand):
    """
    @help: get the URI of current tapis tenant
    """
    async def run(self, *args, **kwargs):
        return self.server.url
    

class manpages(baseCommand.BaseCommand):
    """
    @help: get a link to the application manpages
    """
    async def run(self, *args, **kwargs):
        return "Please see https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/tree/main/icicle_rel_03_2023/CLI/TapisCL-ICICLE for manpages (will add actual manpages later)"