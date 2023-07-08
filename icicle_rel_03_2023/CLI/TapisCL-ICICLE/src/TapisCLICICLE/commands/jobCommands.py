if __name__ != "__main__":
    from . import baseCommand, decorators
    from .arguments import argument
    from . import appCommands
    Argument = argument.Argument


class hide_job(baseCommand.BaseCommand):
    """
    @help: hide a job if its already completed
    """
    required_arguments = [
        Argument('jobUuid')
    ]
    async def run(self, *args, **kwargs):
        return self.t.jobs.hideJob(**kwargs)
    

class unhide_job(hide_job):
    """
    @help: reveal a job previously hidden
    """
    async def run(self, *args, **kwargs):
        return self.t.jobs.unhideJob(**kwargs)
    

class cancel_job(hide_job):
    """
    @help: cancel a job as it executes
    """
    deceorator = decorators.NeedsConfirmation()
    async def run(self, *args, **kwargs):
        return self.t.jobs.cancelJob(**kwargs)
    

class get_job(hide_job):
    """
    @help: get a job and its information
    """
    return_fileds = ['appId', 'appVersion', 'execSystemId', 'uuid']
    async def run(self, *args, **kwargs):
        return self.t.jobs.getJob(**kwargs)
    

class get_job_history(hide_job):
    """
    @help: display the history of changes made to a job
    """
    return_fileds = ['event', 'created']
    optional_arguments = [
        Argument('limit', data_type='int'),
        Argument('skip', data_type='int'),
    ]
    async def run(self, *args, **kwargs):
        return self.t.jobs.getJobHistory(**kwargs)
    

class get_jobs(baseCommand.BaseCommand):
    """
    @help: list all available jobs on the system
    """
    return_fileds = ['appId', 'appVersion', 'execSystemId', 'uuid']
    async def run(self, *args, **kwargs):
        return self.t.jobs.getJobList()
    

class download_job_output(baseCommand.BaseCommand):
    """
    @help: download the job output to an output path
    """
    required_arguments = [
        Argument('jobUuid'),
        Argument('outputPath')
    ]
    optional_arguments = [
        Argument('compress', action='store_true'),
        Argument('format', description='something like zip or tar')
    ]
    async def run(self, *args, **kwargs):
        self.t.jobs.getJobOutputDownload(**kwargs)
        return f"job {kwargs['jobUuid']} output successfully downloaded"
    

class get_job_status(baseCommand.BaseCommand):
    """
    @help: retrieve the status of a job
    """
    required_arguments = [
        Argument('jobUuid')
    ]
    async def run(self, *args, **kwargs):
        return self.t.jobs.getJobStatus(**kwargs)
    

class resubmit_job(baseCommand.BaseCommand):
    """
    @help: resubmit a job with the same arguments as the original submission
    """
    required_arguments = [
        Argument('jobUuid'),
    ]
    async def run(self, *args, **kwargs):
        return self.t.jobs.resubmitJob(**kwargs)
    

class submit_job(appCommands.assign_default_job_attributes):
    """
    @help: submit a job to be run on the select system based on a pre-existing app
    """
    required_arguments = [
        Argument('appId', size_limit=(1, 80), positional=True),
        Argument('appVersion', size_limit=(1, 64), positional=True),
        Argument('name', positional=True)
    ]
    async def run(self, *args, **kwargs):
        return self.t.jobs.submitJob(**kwargs)
    

class share_job(baseCommand.BaseCommand):
    """
    @help: share a job with the select grantee user
    """
    required_arguments = [
        Argument('jobUuid')
    ]
    optional_arguments = [
        Argument('grantee'),
        Argument('jobResource', choices=['JOB_HISTORY', 'JOB_RESUBMIT_REQUEST', 'JOB_OUTPUT', 'JOB_INPUT']),
        Argument('jobPermission', choices=['READ'])
    ]
    async def run(self, *args, **kwargs):
        return self.t.jobs.shareJob(**kwargs)
    

class get_job_share(baseCommand.BaseCommand):
    """
    @help: get sharing information on a specific job
    """
    return_fields = ['jobUuid', 'jobResource', 'grantee']
    required_arguments = [
        Argument('jobUuid')
    ]
    async def run(self, *args, **kwargs):
        return self.t.jobs.getJobShare(**kwargs)
    

class delete_job_share(baseCommand.BaseCommand):
    """
    @help: delete a job sharing
    """
    required_arguments = [
        Argument('jobUuid'),
        Argument('grantee')
    ]
    async def run(self, *args, **kwargs):
        kwargs['user'] = kwargs['grantee']
        kwargs.pop('grantee')
        return self.t.jobs.deleteJobShare(**kwargs)


class subscribe_to_job(baseCommand.BaseCommand):
    """
    @help: subscribe to a job in order to receive notifications on its status by email or such
    """
    required_arguments = [
        Argument('jobUuid'),
        Argument('eventCategoryFilter', choices=[
            'JOB_NEW_STATUS',
            'JOB_INPUT_TRANSACTION_ID',
            'JOB_ARCHIVE_TRANSACTION_ID',
            'JOB_SUBSCRIPTION',
            'JOB_SHARE_EVENT',
            'JOB_ERROR_MESSAGE',
            'JOB_USER_EVENT',
            'ALL'
            ]),
        Argument('deliveryTargets', arg_type='input_list', data_type=argument.Form('deliveryTarget', arguments_list=[
            Argument('deliveryMethod', choices=['WEBHOOK', 'EMAIL', 'QUEUE', 'ACTOR']),
            Argument('deliveryAddress')
        ]))
    ]
    optional_arguments = [
        Argument('description', arg_type='str_input'),
    ]
    async def run(self, *args, **kwargs):
        self.t.jobs.subscribe(**kwargs)
        return f"successfully subscribed to {kwargs['eventCategoryFilter']} event(s) at the selected addresses"
    

class get_subscriptions(baseCommand.BaseCommand):
    """
    @help: list subscriptions
    """
    return_fields = ['name', 'uuid', 'subjectFilter']
    required_arguments = [
        Argument('jobUuid')
    ]
    async def run(self, *args, **kwargs):
        return self.t.jobs.getSubscriptions(**kwargs)
    

class delete_subscriptions(baseCommand.BaseCommand):
    """
    @help: delete a subscription if you no longer want to receive its notifications
    """
    decorator = decorators.NeedsConfirmation()
    required_arguments = [
        Argument('uuid')
    ]
    async def run(self, *args, **kwargs):
        self.t.jobs.deleteSubscriptions(**kwargs)
        return f"subscription {kwargs['uuid']} deleted"