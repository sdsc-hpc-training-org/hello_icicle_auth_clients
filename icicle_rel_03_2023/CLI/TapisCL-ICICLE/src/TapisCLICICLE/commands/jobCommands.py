if __name__ != "__main__":
    from . import baseCommand, decorators
    from .arguments import argument
    Argument = argument.Argument
    

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
