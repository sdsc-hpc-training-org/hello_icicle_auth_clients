if __name__ != "__main__":
    from . import baseCommand
    from .arguments import argument
    from . import decorators
    Argument = argument.Argument


class CHECK_PWD:
    """
    support the invocation of relative paths for tapis systems
    """
    def __init__(self, dir_simplify_args: tuple):
        self.dir_simplify_args = dir_simplify_args

    def __go_back_checker(self, index: int, path_list: list):
        back_count = 0
        for element in path_list[index:]:
            if element != "..":
                break
            back_count += 1
        return back_count

    def __simplify_path(self, path: list):
        index = 0
        length = len(path)
        try:
            while index < length:
                if path[index] == ".":
                    path.pop(index)
                    continue
                elif path[index] == "..":
                    back_count = self.__go_back_checker(index, path)
                    desired_len = len(path) - (2 * back_count)
                    while len(path) != desired_len:
                        path.pop(index-back_count)
                    continue
                index += 1
        except IndexError:
            pass
        finally:
            path = "/".join(path)
            if not path:
                path = "/"
        return path
    
    def __relative_to_absolute(self, absolute_path: str, relative_path: str):
        if not relative_path:
            return absolute_path
        elif absolute_path[-1] == "/":
            return f"{absolute_path}{relative_path}"
        return f"{absolute_path}/{relative_path}"

    def __call__(self, kwargs):
        for file_argument_name in self.dir_simplify_args:
            if not kwargs[file_argument_name] or kwargs['connection'].pwd not in kwargs[file_argument_name]:
                file = self.__relative_to_absolute(kwargs['connection'].pwd, kwargs[file_argument_name])
                kwargs[file_argument_name] = self.__simplify_path(file.split("/"))
        return kwargs
    

class ls(baseCommand.BaseCommand):
    """
    @help: list the files on a system 
    """
    command_opt = [CHECK_PWD(('file_path',))]
    required_arguments = [
        Argument('systemId', size_limit=(1, 80)),
        Argument('file_path', positional=True)
    ]
    async def run(self, *args, **kwargs) -> str: # lists files available on a tapis account
        file_list = self.t.files.listFiles(systemId=kwargs['systemId'], path=kwargs['file_path'])
        file_list_truncated = [f"{file.type} - {file.nativePermissions} ---- {file.name}" for file in file_list]
        return file_list_truncated
    

class cd(baseCommand.BaseCommand):
    """
    @help: change the directory
    """
    command_opt = [CHECK_PWD(('file_path',))]
    required_arguments = [
        Argument('systemId', size_limit=(1, 80)),
        Argument('file_path', positional=True)
    ]
    async def run(self, *args, **kwargs):
        self.t.files.listFiles(systemId=kwargs['systemId'], path=kwargs['file_path'])
        kwargs['connection'].pwd = kwargs['file_path']
        return kwargs['connection'].pwd


class showme(baseCommand.BaseCommand):
    """
    @help: display file metadata
    """
    command_opt = [CHECK_PWD(('file_path',))]
    required_arguments = [
        Argument('systemId', size_limit=(1, 80)),
        Argument('file_path', positional=True)
    ]
    async def run(self, *args, **kwargs):
        return_data = str(self.t.files.getStatInfo(systemId=kwargs['systemId'], path=kwargs['file_path']))
        return return_data
    

class cat(baseCommand.BaseCommand):
    """
    @help: display small files directly to the terminal
    """
    command_opt = [CHECK_PWD(('file_path',))]
    required_arguments = [
        Argument('systemId', size_limit=(1, 80)),
        Argument('file_path', positional=True)
    ]
    async def run(self, *args, **kwargs):
        size = self.t.files.getStatInfo(systemId=kwargs['systemId'], path=kwargs['file_path']).size
        if size <= 4000:
            file_info = self.t.files.getContents(systemId=kwargs['systemId'],
                                path=kwargs['file_path'])
        else:
            file_info = "file too large to print"
        return file_info
    

class mkdir(baseCommand.BaseCommand):
    """
    @help: create a new directory at the selected path
    """
    command_opt = [CHECK_PWD(('file_path',))]
    required_arguments = [
        Argument('systemId', size_limit=(1, 80)),
        Argument('file_path', positional=True)
    ]
    async def run(self, *args, **kwargs):
        self.t.files.mkdir(systemId=kwargs['systemId'], path=kwargs['file_path'])
        return f"Successfully created file at {kwargs['file_path']}"
    

class mv(baseCommand.BaseCommand):
    """
    @help: move a file from a source directory to a destination directory within a system's file structure
    """
    command_opt = [CHECK_PWD(('source_file', 'destination_file'))]
    required_arguments = [
        Argument('systemId', size_limit=(1, 80)),
        Argument('source_file'),
        Argument('desination_file')
    ]
    async def run(self, destination_file: str, *args, **kwargs):
        self.t.files.moveCopy(systemId=kwargs['systemId'], path=kwargs['source_file'], operation="MOVE", newPath=destination_file)
        return f"File moved successfully to {destination_file}"
    

class cp(baseCommand.BaseCommand):
    """
    @help: copy a file from a source directory to another directory
    """
    command_opt = [CHECK_PWD(('source_file', 'destination_file'))]
    required_arguments = [
        Argument('systemId', size_limit=(1, 80)),
        Argument('source_file'),
        Argument('destination_file')
    ]
    async def run(self, *args, **kwargs):
        self.t.files.moveCopy(systemId=kwargs['systemId'], path=kwargs['source_file'], operation="COPY", newPath=kwargs['destination_file'])
        return f"File copied successfully to {kwargs['destination_file']}"
    

class rm(baseCommand.BaseCommand):
    """
    @help: delete a selected file
    """
    decorator=decorators.NeedsConfirmation()
    command_opt = [CHECK_PWD(('file_path',))]
    required_arguments = [
        Argument('systemId', size_limit=(1, 80)),
        Argument('file_path', positional=True)
    ]
    async def run(self, *args, **kwargs):
        self.t.delete(systemId=kwargs['systemId'], path=kwargs['file_path'])
        return f"file {kwargs['file_path']} successfully deleted"
    

class get_recent_transfers(baseCommand.BaseCommand):
    """
    @help: return a list of recent file transfers
    """
    async def run(self, *args, **kwargs):
        recent_transfers = self.t.files.getRecentTransferTasks()
        return str(recent_transfers)
    

class create_postit(baseCommand.BaseCommand):
    """
    @help: create a postit to easily share file with other users
    """
    command_opt = [CHECK_PWD(('file_path',))]
    required_arguments = [
        Argument('systemId', size_limit=(1, 80)),
        Argument('file_path', positional=True)
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
    required_arguments = [
        Argument('postitId'),
    ]
    async def run(self, *args, **kwargs):
        postit = str(self.t.files.getPostIt(postitId=kwargs['postitId']))
        return postit
    

class delete_postit(baseCommand.BaseCommand):
    """
    @help: get a specific postit information based on postit kwargs['systemId']
    """
    required_arguments = [
        Argument('postitId'),
    ]
    async def run(self, *args, **kwargs):
        postit = str(self.t.files.deletePostIt(postitId=kwargs['postitId']))
        return f"Successfully deleted postit {kwargs['postitId']}"
    

class redeem_postit(baseCommand.BaseCommand):
    """
    @help: redeem a postit and download posted file. Downloads to browser
    """
    required_arguments = [
        Argument('postitId'),
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
    command_opt = [CHECK_PWD(('destination_file',))]
    required_arguments = [
        Argument('source_file'),
        Argument('destination_file'),
        Argument('systemId', size_limit=(1, 80))
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
    command_opt = [CHECK_PWD(('source_file',))]
    required_arguments = [
        Argument('source_file'),
        Argument('destination_file'),
        Argument('systemId', size_limit=(1, 80))
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