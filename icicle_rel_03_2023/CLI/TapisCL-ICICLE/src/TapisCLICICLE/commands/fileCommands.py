if __name__ != "__main__":
    from . import baseCommand


def go_back_checker(index, path_list):
    back_count = 0
    for element in path_list[index:]:
        if element != "..":
            break
        back_count += 1
    return back_count

def simplify_path(path):
    index = 0
    length = len(path)
    try:
        while index < length:
            if path[index] == ".":
                path.pop(index)
                continue
            elif path[index] == "..":
                back_count = go_back_checker(index, path)
                desired_len = len(path) - (2 * back_count)
                while len(path) != desired_len:
                    path.pop(index-back_count)
                continue
            index += 1
    except:
        path = "/".join(path)
    return path


class ls(baseCommand.BaseCommand):
    """
    @help: list the files on a system 
    """
    async def run(self, id: str, file: str, *args, **kwargs) -> str: # lists files available on a tapis account
        file_list = self.t.files.listFiles(systemId=id, path=file)
        return file_list
    

class cd(baseCommand.BaseCommand):
    """
    @help: change the directory
    """
    async def run(self, id: str, file: str, *args, **kwargs):
        self.t.files.listFiles(systemId=id, path=file)
        self.server.pwd = file


class showme(baseCommand.BaseCommand):
    """
    @help: display file metadata
    """
    async def run(self, id: str, file: str, *args, **kwargs):
        return_data = str(self.t.files.getStatInfo(systemId=id, path=file))
        return return_data
    

class cat(baseCommand.BaseCommand):
    """
    @help: display small files directly to the terminal
    """
    async def run(self, id: str, file: str, *args, **kwargs):
        size = self.t.files.getStatInfo(systemId=id, path=file).size
        if size <= 4000:
            file_info = self.t.files.getContents(systemId=id,
                                path=file)
        else:
            file_info = "file too large to print"
        return file_info
    

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