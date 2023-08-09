if __name__ != "__main__":
    from . import baseCommand
    from .arguments import argument
    from . import decorators
    from . import commandOpts
    Argument = argument.Argument


class list_clients(baseCommand.BaseCommand):
    """
    @help: list authenticator clients on the current tenant
    """
    return_fields = ['client_id', 'client_key', 'display_name']
    async def run(self, *args, **kwargs):
        return self.t.authenticator.list_clients()
    

class create_client(baseCommand.BaseCommand):
    """
    @help: create a new authenticator client
    """
    return_fields = ['client_id', 'client_key', 'display_name']
    optional_arguments = [
        Argument('client_id'),
        Argument('client_key'),
        Argument('callback_url'),
        Argument('display_name'),
        Argument('description', arg_type='str_input')
    ]
    async def run(self, *args, **kwargs):
        return self.t.authenticator.create_client(**kwargs)
    

class get_client(baseCommand.BaseCommand):
    """
    @help: get client information
    """
    return_fields = ['client_id', 'client_key', 'display_name']
    required_arguments = [
        Argument('client_id')
    ]
    async def run(self, *args, **kwargs):
        return self.t.authenticator.get_client(**kwargs)
    

class update_client(baseCommand.BaseCommand):
    """
    @help: update a client's information
    """
    return_fields = ['client_id', 'client_key', 'display_name']
    required_arguments = [
        Argument('client_id')
    ]
    optional_arguments = [
        Argument('callback_url'),
        Argument('display_name')
    ]
    async def run(self, *args, **kwargs):
        return self.t.authenticator.update_client(**kwargs)
    

class delete_client(baseCommand.BaseCommand):
    """
    @help: delete a client
    """
    required_arguments = [
        Argument('client_id')
    ]
    async def run(self, *args, **kwargs):
        return self.t.authenticator.delete_client(**kwargs)