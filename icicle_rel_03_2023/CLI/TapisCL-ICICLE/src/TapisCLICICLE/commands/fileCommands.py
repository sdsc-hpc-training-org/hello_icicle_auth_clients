if __name__ != "__main__":
    from . import baseCommand


class list_files(baseCommand.BaseCommand):
    """
    @help: list the files on a system 
    """
    async def run(self, id: str, file: str, *args, **kwargs) -> str: # lists files available on a tapis account
        file_list = self.t.files.listFiles(systemId=id, path=file)
        return str(file_list)
    

class upload(baseCommand.BaseCommand):
    """
    @help: upload a file to the system 
    the source and destination files must both be in the file argument, respectively, separated by a comma
    @todo: make it so that this doesnt need to take both source and destination files, but have it so it retrieves the current file location on the tapis system
    and sets that file location to be the upload point. Do the same for downloads but in reverse
    """
    async def run(self, file: str, id: str, *args, **kwargs) -> str: # upload a file from local to remote using tapis. Takes source and destination paths
        source = file.split(",")[0]
        destination = file.split(",")[1]
        self.t.upload(system_id=id,
                source_file_path=source,
                dest_file_path=destination)
        return f'successfully uploaded {source} to {destination}'


class download(baseCommand.BaseCommand):
    """
    @help: download a file from the system
    the source and destination files must both be in the file argument, respectively, separated by a comma
    """
    async def run(self, file: str, id: str, *args, **kwargs) -> str: # download a remote file using tapis, operates basically the same as upload
        source = file.split(",")[0]
        destination = file.split(",")[1]
        file_info = self.t.files.getContents(systemId=id,
                            path=source)

        file_info = file_info.decode('utf-8')
        with open(destination, 'w') as f:
            f.write(file_info)
        return f'successfully downloaded {source} to {destination}'