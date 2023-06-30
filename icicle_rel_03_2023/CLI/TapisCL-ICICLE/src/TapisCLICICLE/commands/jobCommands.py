if __name__ != "__main__":
    from . import baseCommand, decorators
    from .arguments import argument
    Argument = argument.Argument


class hide_job(baseCommand.BaseCommand):
    required_arguments = [
        Argument('jobUuid')
    ]
    async def run(self, *args, **kwargs):
        return self.t.jobs.hideJob(**kwargs)
    

class unhide_Job(hide_job):
    async def run(self, *args, **kwargs):
        return self.t.jobs.unhideJob(**kwargs)
    

class cancel_job(hide_job):
    deceorator = decorators.NeedsConfirmation()
    async def run(self, *args, **kwargs):
        return self.t.jobs.cancelJob(**kwargs)
    

class get_job(hide_job):
    async def run(self, *args, **kwargs):
        return self.t.jobs.getJob(**kwargs)
    

class get_job_history(hide_job):
    optional_arguments = [
        Argument('limit', data_type='int'),
        Argument('skip', data_type='int'),
    ]
    async def run(self, *args, **kwargs):
        return self.t.jobs.getJobHistory(**kwargs)
    

class get_jobs(hide_job):
    async def run(self, *args, **kwargs):
        return self.t.jobs.getJobList()
    

class download_job_output(baseCommand.BaseCommand):
    required_arguments = [
        Argument('jobUuid'),
        Argument('outputPath')
    ]
    optional_arguments = [
        Argument('compress', action='store_true'),
        Argument('format', description='something like zip or tar')
    ]
    async def run(self, *args, **kwargs):
        return self.t.jobs.getJobOutputDownload(**kwargs)
    

class get_job_output_list:
    pass
