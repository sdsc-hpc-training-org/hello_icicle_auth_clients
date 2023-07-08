import json


if __name__ != "__main__":
    from . import baseCommand, decorators
    from .arguments import argument
    Argument = argument.Argument


class create_app(baseCommand.BaseCommand):
    """
    @help: create an app. You must have a properly configured app config file. 
    See a template at https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/tapis-config-files/app-config.json
    """
    supports_config_file=True
    required_arguments = [
        Argument('id', positional=True),
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
    

class update_app(create_app):
    """
    @help: update app with the select attributes
    """
    supports_config_file = True
    required_arguments = [
        Argument('appId', size_limit=(1, 80), positional=True),
        Argument('appVersion', size_limit=(1, 64), positional=True)
    ]
    async def run(self, *args, **kwargs):
        self.t.apps.putApp(**kwargs)
        return f'updated app {kwargs["appId"]} successfully'


class assign_default_job_attributes(baseCommand.BaseCommand):
    """
    @help: assign a default set of job attributes for this app, if you decide to run it as a job
    """
    supports_config_file=True
    required_arguments = [
        Argument('appId', size_limit=(1, 80), positional=True),
        Argument('appVersion', size_limit=(1, 64), positional=True)
    ]
    optional_arguments = [
        Argument('description', arg_type='str_input'),
        Argument('dynamicExecSystem', arg_type='confirmation', description="System is dynamic?"),
        Argument('execSystemConstraints', arg_type='input_list', data_type=Argument('constraint', size_limit=(3, 4096))),
        Argument('execSystemId', size_limit=(1, 80)),
        Argument('execSystemExecDir', size_limit=(1, 4096)),
        Argument('execSystemInputDir', size_limit=(1, 4096)),
        Argument('execSystemOutputDir', size_limit=(1, 4096)),
        Argument('execSystemLogicalQueue', size_limit=(1, 128)),
        Argument('archiveSystemId', size_limit=(1, 80)),
        Argument('archivesystemDir', size_limit=(1, 4096)),
        Argument('archiveOnAppError', arg_type='confirmation', description='archive on error?'),
        Argument("isMpi", arg_type='confirmation', description="is mpi?"),
        Argument('mpiCmd', size_limit=(1, 126), arg_type='str_input'),
        Argument('cmdPrefix', size_limit=(1, 126)),
        argument.Form('parameterSet', arguments_list=[
            Argument('appArgs', arg_type='input_list', data_type=argument.Form('appArg', arguments_list=[
                Argument('name', size_limit=(1, 80)),
                Argument('description', size_limit=(1, 8096)),
                Argument('inputMode', choices=['REQUIRED', "FIXED", "INCLUDE_ON_DEMAND", "INCLUDE_BY_DEFAULT"]),
                Argument('arg')]
            )),
            Argument('containerArgs', arg_type='input_list', data_type=argument.Form('containerArg', arguments_list=[
                Argument('name', size_limit=(1, 80)),
                Argument('description', size_limit=(1, 8096)),
                Argument('inputMode', choices=['REQUIRED', "FIXED", "INCLUDE_ON_DEMAND", "INCLUDE_BY_DEFAULT"]),
                Argument('arg')
            ])),
            Argument('schedulerOptions', arg_type='input_list', data_type=argument.Form('schedulerOption', arguments_list=[
                Argument('name', size_limit=(1, 80)),
                Argument('description', size_limit=(1, 8096)),
                Argument('inputMode', choices=['REQUIRED', "FIXED", "INCLUDE_ON_DEMAND", "INCLUDE_BY_DEFAULT"]),
                Argument('arg')
            ])),
            Argument('envVariables', arg_type='input_list', data_type=argument.Form('environment_variable', arguments_list=[
                Argument('key'),
                Argument('value'),
                Argument('description', size_limit=(1, 2048))
            ]))
        ]),
        Argument('fileInputs', arg_type='input_list', data_type=argument.Form('fileInput', arguments_list=[
            Argument('name', size_limit=(1, 80)),
            Argument('description', size_limit=(1, 8096)),
            Argument('inputMode', choices=['REQUIRED', 'OPTIONAL', 'FIXED']),
            Argument('autoMountLocal', arg_type='confirmation', description='auto mount to local?'),
            Argument('sourceUrl'),
            Argument('targetPath')
        ])),
        Argument('fileInputArrays', arg_type='input_list', data_type=argument.Form('fileInput', arguments_list=[
            Argument('name', size_limit=(1, 80)),
            Argument('description', size_limit=(1, 8096)),
            Argument('inputMode', choices=['REQUIRED', 'OPTIONAL', 'FIXED']),
            Argument('sourceUrls', arg_type='input_list', data_type=Argument('sourceUrl')),
            Argument('targetPath')
        ])),
        Argument('nodeCount', data_type='int'),
        Argument('coresPerNode', data_type='int'),
        Argument('memoryMB', data_type='int'),
        Argument('maxMinutes', data_type='int'),
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
        appId = kwargs.pop('appId')
        appVersion = kwargs.pop('appVersion')
        self.t.apps.putApp(appId=appId, appVersion=appVersion, jobAttributes=kwargs)
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
        print(kwargs)
        if 'appVersion' not in kwargs:
            version = self.t.apps.getAppLatestVersion(**kwargs).version
            kwargs['appVersion'] = version
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