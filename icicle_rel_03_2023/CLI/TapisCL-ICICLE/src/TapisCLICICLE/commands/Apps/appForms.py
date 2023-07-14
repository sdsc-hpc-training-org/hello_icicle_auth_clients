from .. import baseCommand, decorators
from ..arguments import argument
Argument = argument.Argument


CONFIGURE_RUNTIME = argument.Form('configureRuntime', flattening_type='RETRIEVE', required_arguments = [
        Argument('runtime', choices=['SINGULARITY', 'DOCKER']),
        Argument('runtimeVersion')
    ],
    optional_arguments=[
        Argument('runtimeOptions', arg_type='input_list', data_type=Argument('runtimeOption',
            arg_type='str_input', choices=['NONE', 'SINGULARITY_START', 'SINGULARITY_RUN'])),
])

JOB_CONSTRAINTS = argument.Form('configureJobSettings', flattening_type='RETRIEVE', required_arguments = [
    Argument('jobType', choices=['BATCH', 'FORK']),
    Argument('maxJobs', data_type='int'),
    Argument('maxJobsPerUser', data_type='int'),
])

SYSTEM_CONFIG = argument.Form('defaultSystemConfig', flattening_type='RETRIEVE', optional_arguments = [
    Argument('dynamicExecSystem', arg_type='confirmation', description="System is dynamic?"),
    Argument('execSystemConstraints', arg_type='input_list', data_type=Argument('constraint', size_limit=(3, 4096))),
    Argument('execSystemExecDir', size_limit=(1, 4096), description='based on the system job working dir? automatically generated if not specified'),
    Argument('execSystemInputDir', size_limit=(1, 4096), description='what system path will be used to stage input files? automatically generated if not specified'),
    Argument('execSystemOutputDir', size_limit=(1, 4096), description='Where will tapis put job output files? automatically generated if not specified'),
    Argument('execSystemLogicalQueue', size_limit=(1, 128), description='What batch logical queue on the system will be used for execution?'),
])

ARCHIVE_ON_APP_ERROR = argument.Form('archiveOnAppError', flattening_type='FLATTEN',  required_arguments=[
    Argument('archiveSystemId', size_limit=(1, 80), description='What system will be used when archiving outputs?'),
    Argument('archivesystemDir', size_limit=(1, 4096), description='What system directory will be used for archiving?'),
])


APP_ARGUMENTS = Argument('appArgs', arg_type='input_list', data_type=argument.Form('appArg', required_arguments=[
            Argument('name', size_limit=(1, 80)),
            Argument('inputMode', choices=['REQUIRED', "FIXED", "INCLUDE_ON_DEMAND", "INCLUDE_BY_DEFAULT"]),
            Argument('arg')
        ],
        optional_arguments=[
            Argument('description', size_limit=(1, 8096))
        ]
    ), description='command line arguments to be passed to the application', part_of='parameterSet')


CONTAINER_ARGUMENTS = Argument('containerArgs', arg_type='input_list', data_type=argument.Form('containerArg', required_arguments=[
            Argument('name', size_limit=(1, 80)),
            Argument('arg', description='value for the argument'),
            Argument('inputMode', choices=['REQUIRED', "FIXED", "INCLUDE_ON_DEMAND", "INCLUDE_BY_DEFAULT"], description='How will this argument be treated when processing jobs? EG should the job require it?')
        ],
        optional_arguments=[
            Argument('description', size_limit=(1, 8096))
        ]
    ), description='command line arguments to be passed to the container at runtime, whether singularity or container', part_of='parameterSet')


SCHEDULER_OPTIONS = Argument('schedulerOptions', arg_type='input_list', data_type=argument.Form('schedulerOption', required_arguments=[
            Argument('name', size_limit=(1, 80)),
            Argument('inputMode', choices=['REQUIRED', "FIXED", "INCLUDE_ON_DEMAND", "INCLUDE_BY_DEFAULT"]),
            Argument('arg')
        ],
        optional_arguments=[
            Argument('description', size_limit=(1, 8096)),
        ]
    ), description='options to pass to hpc batch scheduler', part_of='parameterSet')


JOB_ENVIRONMENT_VARIABLES = Argument('envVariables', arg_type='input_list', data_type=argument.Form('environment_variable', required_arguments=[
            Argument('key'),
            Argument('value'),
        ],
        optional_arguments=[
            Argument('description', size_limit=(1, 2048))
        ]
    ), description='environment variables placed into the runtime environment', part_of='parameterSet')

JOB_ALLOCATION_CONFIGURATION = argument.Form('jobAllocationConfiguration', flattening_type='RETRIEVE', required_arguments = [
    Argument('nodeCount', data_type='int', description='how many nodes do you want to request in your job?', default_value=1),
    Argument('coresPerNode', data_type='int', description='how many cores per node?', default_value=1),
    Argument('memoryMB', data_type='int', default_value=1),
    Argument('maxMinutes', data_type='int', description='max job runtime in minutes', part_of='parameterSet', default_value=10),
])