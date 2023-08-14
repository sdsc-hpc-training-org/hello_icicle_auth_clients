from tapipy.tapis import errors as TapisErrors


if __name__ != "__main__":
    from . import baseCommand, decorators
    from .arguments import argument
    from . import commandOpts
    Argument = argument.Argument


class get_volumes(baseCommand.BaseCommand):
    """
    @help: get a list of volumes registered to your account
    """
    async def run(self, *args, **kwargs):
        return self.t.pods.get_volumes()
    

class create_volume(baseCommand.BaseCommand):
    """
    @help: create a new volume on which to store files to be used by Tapis pods. This allows several pods to share the same persistent files
    """
    supports_config_file=True
    required_arguments = [
        Argument('volume_id', positional=True)
    ]
    optional_arguments = [
        Argument('description', arg_type='str_input'),
        Argument('size_limit', data_type='int', default_value=1024)
    ]
    async def run(self, *args, **kwargs):
        return self.t.pods.create_volume(**kwargs)
    

class get_volume(baseCommand.BaseCommand):
    """
    @help: get information on a specific volume
    """
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('volume_id')]
    required_arguments = [
        Argument('volume_id', positional=True)
    ]
    async def run(self, *args, **kwargs):
        return self.t.pods.get_volume(**kwargs)
    

class volume(baseCommand.BaseCommand):
    """
    @help: enter the volume to interact with its files more directly
    """
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('volume_id')]
    required_arguments = [
        Argument('volume_id', positional=True)
    ]
    async def run(self, *args, **kwargs):
        volume_info = self.t.pods.get_volume(volume_id=kwargs['volume_id'])
        kwargs['connection'].system = volume_info.volume_id
        kwargs['connection'].pwd = "/"
        return f"successfully entered the volume {kwargs['connection'].system}"
    

class exit_volume(baseCommand.BaseCommand):
    """
    @help: exit the volume you are currently in 
    """
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('volume_id')]
    required_arguments = [
        Argument('volume_id', positional=True)
    ]
    async def run(self, *args, **kwargs):
        kwargs['connection'].system = ""
        kwargs['connection'].pwd = ""
        return f"successfully exited the volume {kwargs['volume_id']}"
    

class update_volume(create_volume):
    """
    @help: update a volume's information
    """
    supports_config_file=True
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('volume_id')]
    async def run(self, *args, **kwargs):
        return self.t.pods.update_volume(**kwargs)
    

class delete_volume(baseCommand.BaseCommand):
    """
    @help: delete a volume
    """
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('volume_id')]
    required_arguments = [
        Argument('volume_id', positional=True),
        Argument('confirm', arg_type='confirmation')
    ]
    async def run(self, *args, **kwargs):
        return self.t.pods.delete_volume_files(**kwargs)


class dir(baseCommand.BaseCommand):
    """
    @help: list all files in the selected volume
    """
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('volume_id')]
    required_arguments = [
        Argument('volume_id', positional=True)
    ]
    async def run(self, *args, **kwargs):
        return self.t.pods.list_volume_files(**kwargs)
    

class upload_volume(baseCommand.BaseCommand):
    """
    @help: upload a file from your local machine to the volume
    """
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('volume_id'), commandOpts.CHECK_PWD(['path'])]
    required_arguments = [
        Argument('volume_id', positional=True),
        Argument('path'),
        Argument('file')
    ]
    async def run(self, *args, **kwargs):
        return self.t.pods.upload_to_volume(**kwargs)
    

class set_volume_permission(baseCommand.BaseCommand):
    """
    @help: set the permission for a user on a volume
    """
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('volume_id')]
    required_arguments = [
        Argument('volume_id', positional=True),
        Argument('username'),
        Argument('level')
    ]
    async def run(self, *args, **kwargs):
        user = kwargs.pop('username')
        kwargs['user'] = user
        return self.t.pods.set_volume_permission(**kwargs)


class get_volume_permissions(baseCommand.BaseCommand):
    """
    @help: set the permission for a user on a volume
    """
    command_opt = [commandOpts.CHECK_EXPLICIT_ID('volume_id')]
    required_arguments = [
        Argument('volume_id', positional=True),
    ]
    async def run(self, *args, **kwargs):
        return self.t.pods.get_volume_permission(**kwargs)
    

class delete_volume_permission(baseCommand.BaseCommand):
    """
    @help: delete the persmission for a user on a volume
    """
    required_arguments = [
        Argument('volume_id', positional=True),
        Argument('username'),
        Argument('level')
    ]
    async def run(self, *args, **kwargs):
        user = kwargs.pop('username')
        kwargs['user'] = user
        return self.t.pods.delete_volume_permission(**kwargs)