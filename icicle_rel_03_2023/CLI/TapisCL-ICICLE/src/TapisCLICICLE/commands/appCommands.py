import json


if __name__ != "__main__":
    from . import baseCommand, decorators
    from .arguments import argument
    Argument = argument.Argument


def get_latest_version(t, kwargs):
    if 'appVersion' not in kwargs:
        version = t.apps.getAppLatestVersion(**kwargs).version
        kwargs['appVersion'] = version
    return kwargs


class create_app(baseCommand.BaseCommand):
    """
    @help: create an app. You must have a properly configured app config file. 
    See a template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/app-config.json
    """
    supports_config_file=True
    required_arguments = [
        Argument('id', positional=True, description='This can be the same as another app as long as the version number is different'),
        Argument('version', positional=True),
        Argument('containerImage')
    ]
    optional_arguments = [
        Argument('description', arg_type='str_input'),
        Argument('owner', default_value=r"${apiUserId}"),
        Argument('enabled', action='store_true'),
        Argument('runtime', choices=['SINGULARITY', 'DOCKER']),
        Argument('runtimeVersion'),
        Argument('runtimeOptions', choices=['NONE', 'SINGULARITY_START', 'SINGULARITY_RUN']),
        Argument('jobType', choices=['BATCH', 'FORK']),
        Argument('maxJobs', data_type='int'),
        Argument('maxJobsPerUser', data_type='int'),
        Argument("strictFileInputs", action='store_true'),
        Argument('tags', arg_type='input_list', data_type=Argument('tag', size_limit=(1, 128))),
    ]
    async def run(self, *args, **kwargs) -> str: # create a tapis app taking a json descriptor file path
        url = self.t.apps.createAppVersion(**kwargs)
        return f"App created successfully\nID: {kwargs['id']}\nVersion: {kwargs['version']}\nURL: {url}\n"
    

class AppUpdatingRetriever(baseCommand.UpdatableFormRetriever):
    def __call__(self, tapis_instance, **kwargs):
        kwargs = get_latest_version(tapis_instance, kwargs)
        app_data = tapis_instance.apps.getApp(appId=kwargs['appId'], appVersion=kwargs['appVersion'])
        return app_data
    

class update_app(create_app):
    """
    @help: update app with the select attributes
    """
    updateable_form_retriever = AppUpdatingRetriever()
    supports_config_file = True
    required_arguments = [
        Argument('appId', size_limit=(1, 80), positional=True),
    ]
    optional_arguments = [
        Argument('appVersion', size_limit=(1, 64)),
        Argument('description', arg_type='str_input'),
        Argument('owner', default_value=r"${apiUserId}"),
        Argument('enabled', action='store_true'),
        Argument('runtime', choices=['SINGULARITY', 'DOCKER']),
        Argument('runtimeVersion'),
        Argument('runtimeOptions', choices=['NONE', 'SINGULARITY_START', 'SINGULARITY_RUN']),
        Argument('jobType', choices=['BATCH', 'FORK']),
        Argument('maxJobs', data_type='int'),
        Argument('maxJobsPerUser', data_type='int'),
        Argument("strictFileInputs", action='store_true'),
        Argument('tags', arg_type='input_list', data_type=Argument('tag', size_limit=(1, 128))),
    ]
    async def run(self, *args, **kwargs):
        kwargs = get_latest_version(self.t, kwargs)
        self.t.apps.patchApp(**kwargs)
        return f'updated app {kwargs["appId"]} successfully'
    

class JobUpdatingRetriever(baseCommand.UpdatableFormRetriever):
    def __call__(self, tapis_instance, **kwargs):
        kwargs = get_latest_version(tapis_instance, kwargs)
        app_data = tapis_instance.apps.getApp(appId=kwargs['appId'], appVersion=kwargs['appVersion']).jobAttributes
        return app_data


class assign_default_job_attributes(baseCommand.BaseCommand):
    """
    @help: assign a default set of job attributes for this app, if you decide to run it as a job
    """
    updateable_form_retriever = JobUpdatingRetriever()
    supports_config_file=True
    required_arguments = [
        Argument('appId', size_limit=(1, 80), positional=True)
    ]
    optional_arguments = [
        Argument('appVersion', size_limit=(1, 64)),
        Argument('description', arg_type='str_input'),
        Argument('dynamicExecSystem', arg_type='confirmation', description="System is dynamic?"),
        Argument('execSystemConstraints', arg_type='input_list', data_type=Argument('constraint', size_limit=(3, 4096))),
        Argument('execSystemId', size_limit=(1, 80), description='what system id will this be run on?'),
        Argument('execSystemExecDir', size_limit=(1, 4096), description='based on the system job working dir? automatically generated if not specified'),
        Argument('execSystemInputDir', size_limit=(1, 4096), description='what system path will be used to stage input files? automatically generated if not specified'),
        Argument('execSystemOutputDir', size_limit=(1, 4096), description='Where will tapis put job output files? automatically generated if not specified'),
        Argument('execSystemLogicalQueue', size_limit=(1, 128), description='What batch logical queue on the system will be used for execution?'),
        Argument('archiveSystemId', size_limit=(1, 80), description='What system will be used when archiving outputs?'),
        Argument('archivesystemDir', size_limit=(1, 4096), description='What system directory will be used for archiving?'),
        Argument('archiveOnAppError', arg_type='confirmation', description='archive on error?'),
        Argument("isMpi", arg_type='confirmation', description="is mpi?"),
        Argument('mpiCmd', size_limit=(1, 126), arg_type='str_input', description='command to launch MPI jobs. Conflicts with cmdPrefix if isMpi is set'),
        Argument('cmdPrefix', size_limit=(1, 126), description='string put in front of app run command to run with mpi command'),
        argument.Form('parameterSet', arguments_list=[
            Argument('appArgs', arg_type='input_list', data_type=argument.Form('appArg', arguments_list=[
                Argument('name', size_limit=(1, 80)),
                Argument('description', size_limit=(1, 8096)),
                Argument('inputMode', choices=['REQUIRED', "FIXED", "INCLUDE_ON_DEMAND", "INCLUDE_BY_DEFAULT"]),
                Argument('arg')]
            ), description='command line arguments to be passed to the application'),
            Argument('containerArgs', arg_type='input_list', data_type=argument.Form('containerArg', arguments_list=[
                Argument('name', size_limit=(1, 80)),
                Argument('description', size_limit=(1, 8096)),
                Argument('inputMode', choices=['REQUIRED', "FIXED", "INCLUDE_ON_DEMAND", "INCLUDE_BY_DEFAULT"], description='How will this argument be treated when processing jobs? EG should the job require it?'),
                Argument('arg', description='value for the argument')
            ]), description='command line arguments to be passed to the container at runtime, whether singularity or container'),
            Argument('schedulerOptions', arg_type='input_list', data_type=argument.Form('schedulerOption', arguments_list=[
                Argument('name', size_limit=(1, 80)),
                Argument('description', size_limit=(1, 8096)),
                Argument('inputMode', choices=['REQUIRED', "FIXED", "INCLUDE_ON_DEMAND", "INCLUDE_BY_DEFAULT"]),
                Argument('arg')
            ]), description='options to pass to hpc batch scheduler'),
            Argument('envVariables', arg_type='input_list', data_type=argument.Form('environment_variable', arguments_list=[
                Argument('key'),
                Argument('value'),
                Argument('description', size_limit=(1, 2048))
            ]), description='environment variables placed into the runtime environment')
        ], description='collections used during job execution. Specify app args, container args, scheduler options, evnironment variables, and archive filter for job execution'),
        Argument('fileInputs', arg_type='input_list', data_type=argument.Form('fileInput', arguments_list=[
            Argument('name', size_limit=(1, 80)),
            Argument('description', size_limit=(1, 8096)),
            Argument('inputMode', choices=['REQUIRED', 'OPTIONAL', 'FIXED'], description='indicates how input should be treeated when processing job request'),
            Argument('autoMountLocal', arg_type='confirmation', description='should the service automatically mount file paths to the containers?'),
            Argument('sourceUrl', description='source used by jobs service when staging file inputs'),
            Argument('targetPath', description='where in the container will the files go when staging the inputs')
        ]), description='selection of file inputs that must be staged to run application'),
        Argument('fileInputArrays', arg_type='input_list', data_type=argument.Form('fileInput', arguments_list=[
            Argument('name', size_limit=(1, 80)),
            Argument('description', size_limit=(1, 8096)),
            Argument('inputMode', choices=['REQUIRED', 'OPTIONAL', 'FIXED']),
            Argument('sourceUrls', arg_type='input_list', data_type=Argument('sourceUrl')),
            Argument('targetPath')
        ]), description='collection of arrays of inputs to be staged to the application'),
        Argument('nodeCount', data_type='int', description='how many nodes do you want to request in your job?'),
        Argument('coresPerNode', data_type='int', description='how many cores per node?'),
        Argument('memoryMB', data_type='int'),
        Argument('maxMinutes', data_type='int', description='max job runtime'),
        Argument('subscriptions', arg_type='input_list', data_type=argument.Form('subscription', arguments_list=[
            Argument('description'),
            Argument('enabled', arg_type='confirmation', description='enable subscription?'),
            Argument('jobEventCategoryFilter', choices=['ALL', 'JOB_NEW_STATUS', 'JOB_INPUT_TRANSACTION_ID', 'JOB_ARCHIVE_TRANSACTION_ID', 'JOB_ERROR_MESSAGE', 'JOB_SUBSCRIPTION']),
            Argument('ttlMinutes', data_type='int'),
            Argument('deliveryTargets', arg_type='input_list', data_type=argument.Form('deliveryTarget', arguments_list=[
                Argument('deliveryMethod', choices=['WEBHOOK', 'EMAIL']),
                Argument('deliveryAddress')
            ]))
        ]))
    ]
    async def run(self, *args, **kwargs):
        kwargs = get_latest_version(self.t, kwargs)
        appId = kwargs.pop('appId')
        appVersion = kwargs.pop('appVersion')
        kwargs.pop('connection')
        jobAttributes = {'jobAttributes':kwargs}
        self.t.apps.patchApp(appId=appId, appVersion=appVersion, **jobAttributes)
        return 'updated job attributes successfully'
    

class get_apps(baseCommand.BaseCommand):
    """
    @help: get a list of all available apps
    """
    return_fields = ['id', 'version']
    optional_arguments = [
        Argument('listType', choices=[
            'OWNED',
            'SHARED_PUBLIC',
            'SHARED_DIRECT',
            'READ_PERM', 
            'MINE',
            'ALL'
        ])
    ]
    async def run(self, *args, **kwargs):
        return self.t.apps.getApps(**kwargs)
    

class get_app(baseCommand.BaseCommand):
    """
    @help: get a specific app
    """
    return_fields = ['id', 'version', 'containerImage']
    required_arguments = [
        Argument('appId', size_limit=(1, 80), positional=True),
    ]
    optional_arguments = [
        Argument('appVersion', size_limit=(1, 64))
    ]
    async def run(self, *args, **kwargs):
        kwargs = get_latest_version(self.t, kwargs)
        return self.t.apps.getApp(**kwargs)
    

class is_app_enabled(baseCommand.BaseCommand):
    """
    @help: check if the app is enabled
    """
    required_arguments = [
        Argument('appId', size_limit=(1, 80), positional=True),
    ]
    async def run(self, *args, **kwargs):
        return self.t.apps.isEnabled(**kwargs)
    

class enable_app(is_app_enabled):
    """
    @help: enable the app
    """
    async def run(self, *args, **kwargs):
        return self.t.apps.enableApp(**kwargs)
    

class disable_app(is_app_enabled):
    """
    @help: disable the app
    """
    async def run(self, *args, **kwargs):
        return self.t.apps.disableApp(**kwargs)
    

class delete_app(is_app_enabled):
    """
    @help: delete the app
    """
    decorator=decorators.NeedsConfirmation()
    async def run(self, *args, **kwargs):
        return self.t.apps.disableApp(**kwargs)
    

class undelete_app(is_app_enabled):
    """
    @help: undo a deletion of an app
    """
    async def run(self, *args, **kwargs):
        return self.t.apps.undeleteApp(**kwargs)
    

class get_app_history(is_app_enabled):
    """
    @help: get the history of changes to an application
    """
    async def run(self, *args, **kwargs):
        return str(self.t.apps.getAppHistory(**kwargs))
    

class get_app_user_perms(baseCommand.BaseCommand):
    """
    @help: get list of user permissions for the app
    """
    required_arguments = [
        Argument('appId', size_limit=(1, 80), positional=True),
        Argument('userName', size_limit=(1, 80))
    ]
    async def run(self, *args, **kwargs):
        return str(self.t.apps.getUserPerms)
    

class grant_app_user_perms(baseCommand.BaseCommand):
    """
    @help: grant user perms for a specific user on an app
    """
    required_arguments = [
        Argument('appId', size_limit=(1, 80), positional=True),
        Argument('userName', size_limit=(1, 80)),
        Argument('permissions', arg_type='input_list', data_type=Argument('permission', choices=['READ', 'MODIFY', 'EXECUTE']))
    ]
    async def run(self, *args, **kwargs):
        return self.t.apps.grantUserPerms(**kwargs)
    

class revoke_app_user_perms(grant_app_user_perms):
    """
    @help: revoke perms for a specific user on an app
    """
    async def run(self, *args, **kwargs):
        return self.t.apps.revokeUserPerms(**kwargs)