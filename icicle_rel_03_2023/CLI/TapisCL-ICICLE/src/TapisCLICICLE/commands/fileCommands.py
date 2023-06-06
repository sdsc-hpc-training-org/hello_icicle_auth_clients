if __name__ != "__main__":
    from . import baseCommand
    from . import args
    from . import decorators


class CHECK_PWD:
    """
    support the invocation of relative paths for tapis systems
    """
    def __init__(self, dir_simplify_args: tuple):
        for arg in dir_simplify_args:
            if arg not in list(args.Args.argparser_args.keys()):
                raise AttributeError(f"The argument {arg} is not in the args file!")
        self.dir_simplify_args = dir_simplify_args

    def __go_back_checker(self, index, path_list):
        back_count = 0
        for element in path_list[index:]:
            if element != "..":
                break
            back_count += 1
        return back_count

    def __simplify_path(self, path):
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
        except:
            path = "/".join(path)
        return path

    def __call__(self, kwargs):
        for arg in self.dir_simplify_args:
            if not kwargs[arg]:
                kwargs[arg] = ''
            if not kwargs[arg] or kwargs['server'].pwd not in kwargs[arg]:
                file = kwargs['server'].pwd + kwargs[arg]
                kwargs[arg] = self.__simplify_path(file)
        return kwargs
    

class ls(baseCommand.BaseCommand):
    """
    @help: list the files on a system 
    """
    command_opt = [CHECK_PWD(('file'))]
    async def run(self, id: str, file: str, *args, **kwargs) -> str: # lists files available on a tapis account
        file_list = self.t.files.listFiles(systemId=id, path=file)
        file_list_truncated = []
        for file in file_list:
            file_list_truncated.append(f"{file.type} - {file.nativePermissions} ---- {file.name}")
        return file_list_truncated
    

class cd(baseCommand.BaseCommand):
    """
    @help: change the directory
    """
    command_opt = [CHECK_PWD(('file'))]
    async def run(self, id: str, file: str, *args, **kwargs):
        self.t.files.listFiles(systemId=id, path=file)
        self.server.pwd = file
        return self.server.pwd


class showme(baseCommand.BaseCommand):
    """
    @help: display file metadata
    """
    command_opt = [CHECK_PWD(('file'))]
    async def run(self, id: str, file: str, *args, **kwargs):
        return_data = str(self.t.files.getStatInfo(systemId=id, path=file))
        return return_data
    

class cat(baseCommand.BaseCommand):
    """
    @help: display small files directly to the terminal
    """
    command_opt = [CHECK_PWD(('file'))]
    async def run(self, id: str, file: str, *args, **kwargs):
        size = self.t.files.getStatInfo(systemId=id, path=file).size
        if size <= 4000:
            file_info = self.t.files.getContents(systemId=id,
                                path=file)
        else:
            file_info = "file too large to print"
        return file_info
    

class mkdir(baseCommand.BaseCommand):
    """
    @help: create a new directory at the selected path
    """
    command_opt = [CHECK_PWD(('file'))]
    async def run(self, id: str, file: str, *args, **kwargs):
        self.t.files.mkdir(systemId=id, path=file)
        return f"Successfully created file at {file}"
    

class mv(baseCommand.BaseCommand):
    """
    @help: move a file from a source directory to a destination directory within a system's file structure
    """
    command_opt = [CHECK_PWD(('source_file', 'destination_file'))]
    async def run(self, id: str, source_file: str, destination_file: str, *args, **kwargs):
        self.t.files.moveCopy(systemId=id, path=source_file, operation="MOVE", newPath=destination_file)
        return f"File moved successfully to {destination_file}"
    

class cp(baseCommand.BaseCommand):
    """
    @help: copy a file from a source directory to another directory
    """
    command_opt = [CHECK_PWD(('source_file', 'destination_file'))]
    async def run(self, id: str, source_file: str, destination_file: str, *args, **kwargs):
        self.t.files.moveCopy(systemId=id, path=source_file, operation="COPY", newPath=destination_file)
        return f"File copied successfully to {destination_file}"
    

class rm(baseCommand.BaseCommand):
    """
    @help: delete a selected file
    """
    decorator=decorators.NeedsConfirmation
    command_opt = [CHECK_PWD(('file'))]
    async def run(self, id: str, file: str, *args, **kwargs):
        self.t.delete(systemId=id, path=file)
        return f"file {file} successfully deleted"
    

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
    decorator=decorators.RequiresForm
    command_opt = [CHECK_PWD(('file'))]
    async def run(self, id: str, file: str, allowed_uses=1, expiration_time=2592000, *args, **kwargs):
        self.t.files.createPostIt(systemId=id, path=file, allowedUses=allowed_uses, validSeconds=expiration_time)
        return f"created a postit for the file {file}"
    

class list_postits(baseCommand.BaseCommand):
    """
    @help: list all postits
    """
    decorator=decorators.RequiresForm
    async def run(self, OWNED_or_ALL="ALL", *args, **kwargs):
        postit_list = str(self.t.files.listPostIts(listType=OWNED_or_ALL))
        return postit_list
    

class get_postit(baseCommand.BaseCommand):
    """
    @help: get a specific postit information based on postit id
    """
    async def run(self, id, *args, **kwargs):
        postit = str(self.t.files.getPostIt(postitId=id))
        return postit
    

class delete_postit(baseCommand.BaseCommand):
    """
    @help: get a specific postit information based on postit id
    """
    async def run(self, id, *args, **kwargs):
        postit = str(self.t.files.deletePostIt(postitId=id))
        return f"Successfully deleted postit {id}"
    

class redeem_postit(baseCommand.BaseCommand):
    """
    @help: redeem a postit and download posted file. Downloads to browser
    """
    async def run(self, id, *args, **kwargs):
        self.t.files.redeemPostIt(postitId=id)
        return f"Downloading postit {id}, check browser"

    
class upload(baseCommand.BaseCommand):
    """
    @help: upload a file to the system 
    the source and destination files must both be in the file argument, respectively, separated by a comma
    @todo: make it so that this doesnt need to take both source and destination files, but have it so it retrieves the current file location on the tapis system
    and sets that file location to be the upload point. Do the same for downloads but in reverse
    """
    async def run(self, source_file, destination_file, id: str, *args, **kwargs) -> str: # upload a file from local to remote using tapis. Takes source and destination paths
        if not destination_file:
            destination_file = self.server.pwd
        self.t.upload(system_id=id,
                source_file_path=source_file,
                dest_file_path=destination_file)
        return f'successfully uploaded {source_file} to {destination_file}'


class download(baseCommand.BaseCommand):
    """
    @help: download a file from the system
    the source and destination files must both be in the file argument, respectively, separated by a comma
    """
    async def run(self, source_file: str, destination_file: str, id: str, *args, **kwargs) -> str: # download a remote file using tapis, operates basically the same as upload
        if not source_file:
            source_file = self.server.pwd
        file_info = self.t.files.getContents(systemId=id,
                            path=source_file)
        file_info = file_info.decode('utf-8')
        with open(destination_file, 'w') as f:
            f.write(file_info)
        return f'successfully downloaded {source_file} to {destination_file}'