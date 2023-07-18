if __name__ != "__main__":
    from . import baseCommand
    from .arguments import argument
    from . import decorators
    from . import commandOpts
    Argument = argument.Argument


class ls(baseCommand.BaseCommand):
    """
    @help: list the files on a system 
    """
    command_opt = [commandOpts.CHECK_PWD(('file_path',)), commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('file_path', positional=True),
        Argument('systemId', size_limit=(1, 80), positional=True)
    ]
    async def run(self, *args, **kwargs) -> str: # lists files available on a tapis account
        file_list = self.t.files.listFiles(systemId=kwargs['systemId'], path=kwargs['file_path'])
        file_list_truncated = [f"{file.type} - {file.nativePermissions} ---- {file.name}" for file in file_list]
        return file_list_truncated
    

class cd(baseCommand.BaseCommand):
    """
    @help: change the directory
    """
    command_opt = [commandOpts.CHECK_PWD(('file_path',)), commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('file_path', positional=True),
        Argument('systemId', size_limit=(1, 80), positional=True)
    ]
    async def run(self, *args, **kwargs):
        self.t.files.listFiles(systemId=kwargs['systemId'], path=kwargs['file_path'])
        kwargs['connection'].pwd = kwargs['file_path']
        return kwargs['connection'].pwd
    

class pwd(baseCommand.BaseCommand):
    """
    @help: get the current directory
    """
    async def run(self, *args, **kwargs):
        return kwargs['connection'].pwd

class showme(baseCommand.BaseCommand):
    """
    @help: display file metadata
    """
    command_opt = [commandOpts.CHECK_PWD(('file_path',)), commandOpts.CHECK_EXPLICIT_ID('systemId')]
    return_fields = ['absolutePath', 'uid', 'size', 'perms']
    required_arguments = [
        Argument('file_path', positional=True),
        Argument('systemId', size_limit=(1, 80), positional=True)
    ]
    async def run(self, *args, **kwargs):
        return_data = self.t.files.getStatInfo(systemId=kwargs['systemId'], path=kwargs['file_path'])
        return return_data
    

class cat(baseCommand.BaseCommand):
    """
    @help: display small files directly to the terminal
    """
    command_opt = [commandOpts.CHECK_PWD(('file_path',)), commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('file_path', positional=True),
        Argument('systemId', size_limit=(1, 80), positional=True)
    ]
    async def run(self, *args, **kwargs):
        size = self.t.files.getStatInfo(systemId=kwargs['systemId'], path=kwargs['file_path']).size
        if size <= 4096:
            file_info = self.t.files.getContents(systemId=kwargs['systemId'],
                                path=kwargs['file_path'])
        else:
            file_info = "file too large to print"
        return file_info
    

class mkdir(baseCommand.BaseCommand):
    """
    @help: create a new directory at the selected path
    """
    command_opt = [commandOpts.CHECK_PWD(('file_path',)), commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('file_path', positional=True),
        Argument('systemId', size_limit=(1, 80), positional=True)
    ]
    async def run(self, *args, **kwargs):
        self.t.files.mkdir(systemId=kwargs['systemId'], path=kwargs['file_path'])
        return f"Successfully created file at {kwargs['file_path']}"
    

class mv(baseCommand.BaseCommand):
    """
    @help: move a file from a source directory to a destination directory within a system's file structure
    """
    command_opt = [commandOpts.CHECK_PWD(('source_file', 'destination_file')), commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('source_file', positional=True),
        Argument('systemId', size_limit=(1, 80), positional=True),
        Argument('desination_file')
    ]
    async def run(self, destination_file: str, *args, **kwargs):
        self.t.files.moveCopy(systemId=kwargs['systemId'], path=kwargs['source_file'], operation="MOVE", newPath=destination_file)
        return f"File moved successfully to {destination_file}"
    

class cp(baseCommand.BaseCommand):
    """
    @help: copy a file from a source directory to another directory
    """
    command_opt = [commandOpts.CHECK_PWD(('source_file', 'destination_file')), commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('source_file', positional=True),
        Argument('systemId', size_limit=(1, 80), positional=True),
        Argument('destination_file')
    ]
    async def run(self, *args, **kwargs):
        self.t.files.moveCopy(systemId=kwargs['systemId'], path=kwargs['source_file'], operation="COPY", newPath=kwargs['destination_file'])
        return f"File copied successfully to {kwargs['destination_file']}"
    

class rm(baseCommand.BaseCommand):
    """
    @help: delete a selected file
    """
    command_opt = [commandOpts.CHECK_PWD(('file_path',)), commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('file_path', positional=True),
        Argument('systemId', size_limit=(1, 80), positional=True)
    ]
    async def run(self, *args, **kwargs):
        self.t.delete(systemId=kwargs['systemId'], path=kwargs['file_path'])
        return f"file {kwargs['file_path']} successfully deleted"
    

class get_recent_transfers(baseCommand.BaseCommand):
    """
    @help: return a list of recent file transfers
    """
    return_fields = ['id', 'username', 'status', 'estimatedTotalBytes']
    async def run(self, *args, **kwargs):
        recent_transfers = self.t.files.getRecentTransferTasks()
        return recent_transfers
    

class create_transfer_task(baseCommand.BaseCommand):
    """
    @help: create a task to transfer files between systems. The two system types must be the same
    """
    required_arguments = [
        Argument('source_file_path', positional=True),
        Argument('source_system_id', positional=True),
        Argument('destination_system_id'),
        Argument('destination_file_path')
    ]
    async def run(self, *args, **kwargs):
        pass
    

class create_postit(baseCommand.BaseCommand):
    """
    @help: create a postit to easily share file with other users
    """
    return_fields = ['postitId', 'systemId', 'path', 'redeemUrl']
    command_opt = [commandOpts.CHECK_PWD(('file_path',)), commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('file_path', positional=True),
        Argument('systemId', size_limit=(1, 80), positional=True)
    ]
    optional_arguments = [
        Argument('allowed_uses', data_type='int'),
        Argument('expiration_time', data_type='int')
    ]
    async def run(self, *args, **kwargs):
        self.t.files.createPostIt(systemId=kwargs['systemId'], path=kwargs['file_path'], allowedUses=kwargs['allowed_uses'], validSeconds=kwargs['expiration_time'])
        return f"created a postit for the file {kwargs['file_path']}"
    

class list_postits(baseCommand.BaseCommand):
    """
    @help: list all postits
    """
    return_fields = ['postitId', 'systemId', 'path', 'redeemUrl']
    optional_arguments = [
        Argument('owned_or_all', choices=['ALL', 'OWNED'])
    ]
    async def run(self, *args, **kwargs):
        postit_list = str(self.t.files.listPostIts(listType=kwargs['owned_or_all']))
        return postit_list
    

class get_postit(baseCommand.BaseCommand):
    """
    @help: get a specific postit information based on postit id
    """
    return_fields = ['postitId', 'systemId', 'path', 'redeemUrl']
    required_arguments = [
        Argument('postitId', positional=True),
    ]
    async def run(self, *args, **kwargs):
        postit = str(self.t.files.getPostIt(postitId=kwargs['postitId']))
        return postit
    

class delete_postit(baseCommand.BaseCommand):
    """
    @help: get a specific postit information based on postit kwargs['systemId']
    """
    required_arguments = [
        Argument('postitId', positional=True),
    ]
    async def run(self, *args, **kwargs):
        postit = str(self.t.files.deletePostIt(postitId=kwargs['postitId']))
        return f"Successfully deleted postit {kwargs['postitId']}"
    

class redeem_postit(baseCommand.BaseCommand):
    """
    @help: redeem a postit and download posted file. Downloads to browser
    """
    required_arguments = [
        Argument('postitId', positional=True),
    ]
    async def run(self, *args, **kwargs):
        self.t.files.redeemPostIt(postitId=kwargs['postitId'])
        return f"Downloading postit {kwargs['postitId']}, check browser"

    
class upload(baseCommand.BaseCommand):
    """
    @help: upload a file to the system 
    the source and destination files must both be in the file argument, respectively, separated by a comma
    @todo: make it so that this doesnt need to take both source and destination files, but have it so it retrieves the current file location on the tapis system
    and sets that file location to be the upload point. Do the same for downloads but in reverse
    """
    command_opt = [commandOpts.CHECK_PWD(('destination_file',)), commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('source_file', positional=True),
        Argument('systemId', size_limit=(1, 80), positional=True),
        Argument('destination_file'),
    ]
    async def run(self, *args, **kwargs) -> str: # upload a file from local to remote using tapis. Takes source and destination paths
        if not kwargs['destination_file']:
            kwargs['destination_file'] = kwargs['connection'].pwd
        self.t.upload(system_id=kwargs['systemId'],
                source_file_path=kwargs['source_file'],
                dest_file_path=kwargs['destination_file'])
        return f'successfully uploaded {kwargs["source_file"]} to {kwargs["destination_file"]}'


class download(baseCommand.BaseCommand):
    """
    @help: download a file from the system
    the source and destination files must both be in the file argument, respectively, separated by a comma
    """
    command_opt = [commandOpts.CHECK_PWD(('source_file',)), commandOpts.CHECK_EXPLICIT_ID('systemId')]
    required_arguments = [
        Argument('source_file', positional=True),
        Argument('systemId', size_limit=(1, 80), positional=True),
        Argument('destination_file'),
        Argument('connection', arg_type='silent')
    ]
    async def run(self, *args, **kwargs) -> str: # download a remote file using tapis, operates basically the same as upload
        if not kwargs["source_file"]:
            kwargs["source_file"] = kwargs['connection'].pwd
        file_info = self.t.files.getContents(systemId=kwargs['systemId'],
                            path=kwargs["source_file"])
        file_info = file_info.decode('utf-8')
        with open(kwargs['destination_file'], 'w') as f:
            f.write(file_info)
        return f'successfully downloaded {kwargs["source_file"]} to {kwargs["destination_file"]}'
    

