from tapipy import tapis
import pyperclip
import json
try:
    from . import baseCommand
    from ..utilities import decorators
except:
    import commands.baseCommand as baseCommand
    import utilities.decorators as decorators


class create_app(baseCommand.BaseCommand):
    """
    @help: create an app. You must have a properly configured app config file. 
    See a template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/app-config.json
    @todo: add a system where the class can say whether or not the config file of the app exists, and if it does not, open up a form to get system information. Maybe 
    be able to run RequiresForm as something other than a decorator?
    """
    async def run(self, file: str, *args, **kwargs) -> str: # create a tapis app taking a json descriptor file path
        with open(file, 'r') as f:
            app_def = json.loads(f.read())
        url = self.t.apps.createAppVersion(**app_def)
        return f"App created successfully\nID: {app_def['id']}\nVersion: {app_def['version']}\nURL: {url}\n"


class get_apps(baseCommand.BaseCommand):
    """
    @help: get all the apps on a system
    """
    async def run(self, *args, **kwargs) -> str:
        apps = self.t.apps.getApps()
        return str(apps)


class delete_app(baseCommand.BaseCommand):
    """
    @help: delete the selected app
    """
    decorator=decorators.NeedsConfirmation()
    async def run(self, id: str, version: str, *args, **kwargs) -> str:
        return_value = self.t.apps.deleteApp(appId=id, appVersion=version)
        return str(return_value)


class get_app(baseCommand.BaseCommand):
    """
    @help: return selected app information
    """
    async def run(self, verbose: bool, id: str, version: str, *args, **kwargs)-> None | str: # returns app information with an id and version as arguments
        app = self.t.apps.getApp(appId=id, appVersion=version)
        if verbose:
            return str(app)
        return None
    

class run_job(baseCommand.BaseCommand):
    """
    @help: run a job from an app on a system. You must have a properly configured job config file. 
    See a template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/job-config.json
    """
    async def run(self, file: str, *args, **kwargs)->str: # run a job using an app. Takes a job descriptor json file path
        with open(file, 'r') as f:
            app = json.loads(f.read())
        job = self.t.jobs.submitJob(**app)
        return str(job.uuid)


class get_job_status(baseCommand.BaseCommand):
    """
    @help: get the status of a job
    """
    async def run(self, uuid: str, *args, **kwargs)->str: # return a job status with its Uuid
        job_status = self.t.jobs.getJobStatus(jobUuid=uuid)
        return str(job_status)


class download_job_output(baseCommand.BaseCommand):
    """
    @help: download a job output from the system 
    """
    async def run(self, uuid: str, file: str, *args, **kwargs)->str: # download the output of a job with its Uuid
        jobs_output = self.t.jobs.getJobOutputDownload(jobUuid=uuid, outputPath='tapisjob.out')
        with open(file, 'w') as f:
            f.write(jobs_output)
        return f"Successfully downloaded job output to {file}"
