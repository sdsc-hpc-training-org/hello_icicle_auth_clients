from .. import baseCommand, decorators
from ..arguments import argument
Argument = argument.Argument


CONFIGURE_RUNTIME = argument.Form('configureRuntime', flattening_type='RETRIEVE', arguments_list = [
    Argument('runtime', choices=['SINGULARITY', 'DOCKER']),
    Argument('runtimeVersion'),
    Argument('runtimeOptions', arg_type='input_list', data_type=Argument('runtimeOption',
        arg_type='str_input', choices=['NONE', 'SINGULARITY_START', 'SINGULARITY_RUN'])),
])

CONFIGURE_JOB_SETTINGS = argument.Form('configureJobSettings', flattening_type='RETRIEVE', arguments_list = [
    Argument('jobType', choices=['BATCH', 'FORK']),
    Argument('maxJobs', data_type='int'),
    Argument('maxJobsPerUser', data_type='int'),
])

SYSTEM_CONFIG = argument.Form('defaultSystemConfig', flattening_type='RETRIEVE', arguments_list = [
    Argument('dynamicExecSystem', arg_type='confirmation', description="System is dynamic?"),
    Argument('execSystemConstraints', arg_type='input_list', data_type=Argument('constraint', size_limit=(3, 4096))),
    Argument('execSystemId', size_limit=(1, 80), description='what system id will this be run on?'),
    Argument('execSystemExecDir', size_limit=(1, 4096), description='based on the system job working dir? automatically generated if not specified'),
    Argument('execSystemInputDir', size_limit=(1, 4096), description='what system path will be used to stage input files? automatically generated if not specified'),
    Argument('execSystemOutputDir', size_limit=(1, 4096), description='Where will tapis put job output files? automatically generated if not specified'),
    Argument('execSystemLogicalQueue', size_limit=(1, 128), description='What batch logical queue on the system will be used for execution?'),
])

ARCHIVE_ON_APP_ERROR = argument.Form('archiveOnAppError', flattening_type='FLATTEN',  arguments_list=[
    Argument('archiveSystemId', size_limit=(1, 80), description='What system will be used when archiving outputs?'),
    Argument('archivesystemDir', size_limit=(1, 4096), description='What system directory will be used for archiving?'),
])

PARAMETER_SET = argument.Form('parameterSet', arguments_list=[
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
], description='collections used during job execution. Specify app args, container args, scheduler options, evnironment variables, and archive filter for job execution')

JOB_ALLOCATION_CONFIGURATION = argument.Form('jobAllocationConfiguration', flattening_type='RETRIEVE', arguments_list = [
    Argument('nodeCount', data_type='int', description='how many nodes do you want to request in your job?'),
    Argument('coresPerNode', data_type='int', description='how many cores per node?'),
    Argument('memoryMB', data_type='int'),
    Argument('maxMinutes', data_type='int', description='max job runtime'),
])