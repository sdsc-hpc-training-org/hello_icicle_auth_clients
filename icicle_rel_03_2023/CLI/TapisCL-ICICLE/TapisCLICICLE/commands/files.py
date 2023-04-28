try:
    from . import baseWrappers
except:
    import commands.baseWrappers as baseWrappers


class Files(baseWrappers.tapisObject):
    """
    @help: Access Tapis files through the connected service
    """
    def __init__(self, tapis_instance, username, password, connection=None):
        command_map = {
            'list_files':self.list_files,
            'upload':self.upload,
            'download':self.download,
            'help':self.help
        }
        super().__init__(tapis_instance, username, password, connection=connection, command_map=command_map)

    def return_formatter(self, info):
        return f"name: {info.name}\ngroup: {info.group}\npath: {info.path}\n"

    def list_files(self, verbose: bool, id: str, file: str, connection=None) -> str: # lists files available on a tapis account
        """
        @help: list the files on a system 
        """
        file_list = self.t.files.listFiles(systemId=id, path=file)
        if verbose:
            return str(file_list)
        file_list = [self.return_formatter(f) for f in file_list]
        return str(file_list)

    def upload(self, file: str, id: str, connection=None) -> str: # upload a file from local to remote using tapis. Takes source and destination paths
        """
        @help: upload a file to the system 
        the source and destination files must both be in the file argument, respectively, separated by a comma
        """
        source = file.split(",")[0]
        destination = file.split(",")[1]
        self.t.upload(system_id=id,
                source_file_path=source,
                dest_file_path=destination)
        return f'successfully uploaded {source} to {destination}'
            
    def download(self, file: str, id: str, connection=None) -> str: # download a remote file using tapis, operates basically the same as upload
        """
        @help: download a file from the system
        the source and destination files must both be in the file argument, respectively, separated by a comma
        """
        source = file.split(",")[0]
        destination = file.split(",")[1]
        file_info = self.t.files.getContents(systemId=id,
                            path=source)

        file_info = file_info.decode('utf-8')
        with open(destination, 'w') as f:
            f.write(file_info)
        return f'successfully downloaded {source} to {destination}'
