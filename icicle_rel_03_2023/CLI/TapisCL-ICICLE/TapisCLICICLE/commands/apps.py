import json
try:
    from ..utilities import decorators
    from . import baseWrappers
except:
    import utilities.decorators as decorators
    import commands.baseWrappers as baseWrappers


class Apps(baseWrappers.tapisObject):
    """
    @help: Access Tapis systems through the connected service
    """
    def __init__(self, tapis_instance, username, password, connection=None):
        command_map = {
            'create_app':self.create_app,
            'get_apps':self.get_apps,
            'delete_app':self.delete_app,
            'get_app_info':self.get_app,
            'run_app':self.run_job,
            'get_app_status':self.get_job_status,
            'download_app_results':self.download_job_output,
            'help':self.help,
        }
        super().__init__(tapis_instance, username, password, connection=connection, command_map=command_map)

    async def create_app(self, file: str, connection=None) -> str: # create a tapis app taking a json descriptor file path
        """
        @help: create an app. You must have a properly configured app config file. 
        See a template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/app-config.json
        """
        with open(file, 'r') as f:
            app_def = json.loads(f.read())
        url = self.t.apps.createAppVersion(**app_def)
        return f"App created successfully\nID: {app_def['id']}\nVersion: {app_def['version']}\nURL: {url}\n"

    async def get_apps(self, connection=None) -> str:
        """
        @help: get all the apps on a system
        """
        apps = self.t.apps.getApps()
        return str(apps)

    @decorators.NeedsConfirmation
    async def delete_app(self, id: str, version: str, connection=None) -> str:
        """
        @help: delete the selected app
        """
        return_value = self.t.apps.deleteApp(appId=id, appVersion=version)
        return str(return_value)

    async def get_app(self, verbose: bool, id: str, version: str, connection=None)-> None | str: # returns app information with an id and version as arguments
        """
        @help: return selected app information
        """
        app = self.t.apps.getApp(appId=id, appVersion=version)
        if verbose:
            return str(app)
        return None

    async def run_job(self, file: str, connection=None)->str: # run a job using an app. Takes a job descriptor json file path
        """
        @help: run a job from an app on a system. You must have a properly configured job config file. 
        See a template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/job-config.json
        """
        with open(file, 'r') as f:
            app = json.loads(f.read())
        job = self.t.jobs.submitJob(**app)
        return str(job.uuid)

    async def get_job_status(self, uuid: str, connection=None)->str: # return a job status with its Uuid
        """
        @help: get the status of a job
        """
        job_status = self.t.jobs.getJobStatus(jobUuid=uuid)
        return str(job_status)

    async def download_job_output(self, uuid: str, file: str, connection=None)->str: # download the output of a job with its Uuid
        """
        @help: download a job output from the system 
        """
        jobs_output = self.t.jobs.getJobOutputDownload(jobUuid=uuid, outputPath='tapisjob.out')
        with open(file, 'w') as f:
            f.write(jobs_output)
        return f"Successfully downloaded job output to {file}"