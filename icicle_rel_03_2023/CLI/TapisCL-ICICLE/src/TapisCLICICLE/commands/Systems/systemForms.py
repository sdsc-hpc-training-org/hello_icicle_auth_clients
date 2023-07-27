from .. import baseCommand, decorators
from ..arguments import argument
from .. import commandOpts
from socketopts import schemas
Argument = argument.Argument


CAN_EXEC = argument.Form('canExec', flattening_type='FLATTEN', required_arguments=[
    Argument('jobRuntimes', arg_type='input_list', data_type=argument.Form(
    'jobRuntime', required_arguments= [
        Argument('runtimeType', choices=['DOCKER', 'SINGULARITY'])
    ],
    optional_arguments = [
        Argument('version')
    ]
    )),
    Argument('jobWorkingDir', default_value=r"HOST_EVAL($WORK2)", size_limit=(0, 4096), description='Where on this hpc system are jobs run?'),
])

USE_PROXY = argument.Form('useProxy', flattening_type='FLATTEN', required_arguments = [
    Argument('proxyHost', size_limit=(0, 256)),
    Argument('proxyPort', data_type='int'),
])

CAN_RUN_BATCH = argument.Form('canRunBatch', flattening_type='FLATTEN', required_arguments = [
    Argument('batchScheduler', choices=['SLURM', "CONDOR", "PBS", "SGE", "UGE", "TORQUE"], default_value='SLURM'),
    Argument('batchSchedulerProfile'),
    Argument('batchLogicalQueues', arg_type='input_list', data_type=argument.Form(
        'batchLogicalQueue', required_arguments = [
            Argument('name', size_limit=(1, 128)),
            Argument('hpcQueueName', size_limit=(1, 128)),
            Argument('maxJobs', data_type='int', default_value=50),
            Argument('maxJobsPerUser', data_type='int', default_value=10),
            Argument('minNodeCount', data_type='int', default_value=1),
            Argument('maxNodeCount', data_type='int', default_value=16),
            Argument('minCoresPerNode', data_type='int', default_value=1),
            Argument('maxCoresPerNode', data_type='int', default_value=16),
            Argument('minMemoryMB', data_type='int', default_value=1),
            Argument('maxMemoryMB', data_type='int', default_value=16384),
            Argument('minMinutes', data_type='int', default_value=1),
            Argument('maxMinutes', data_type='int', default_value=60)
        ]
    ))],
    optional_arguments = [
        Argument('batchDefaultLogicalQueue', size_limit=(1, 128)),
    ])

MOUNT_DATA_TRANSFER_NODE = argument.Form('mountDataTransferNode', flattening_type='RETRIEVE', required_arguments=[
    Argument('dtnSystemId', size_limit=(0, 80)),
    Argument('dtnMountPoint'),
    Argument('dtnMountSourcePath')
])

JOB_ENVIRONMENT_VARIABLES = Argument('jobEnvVariables', arg_type='input_list', data_type=argument.Form(
        'jobEnvironmentVariable', required_arguments = [
            Argument('key'),
            Argument('value', default_value=''),
        ],
        optional_arguments = [
            Argument('description', size_limit=(0, 2048), arg_type='str_input')
        ]
    ))

JOB_CAPABILITIES = Argument('jobCapabilities', arg_type='input_list', data_type=argument.Form(
            'jobCapability', required_arguments=[
                Argument('name', size_limit=(1, 128)),
                Argument('value'),
                Argument('category', choices=['SCHEUDLER', 
                                            'OS', 'HARDWARE', 
                                            'SOFTWARE', 'JOB', 
                                            'CONTAINER', 'MISC', 
                                            'CUSTOM']),
                Argument('datatype', choices=['STRING', 'INTEGER', 
                                            'BOOLEAN', 'NUMBER', 
                                            'TIMESTAMP']),
                Argument('precedence', data_type='int'),
        ]
    ))

JOB_CONSTRAINTS = argument.Form('jobConstraints', flattening_type='RETRIEVE', depends_on=['canExec'], required_arguments=[
        Argument('jobMaxJobs', data_type='int'),
        Argument('jobMaxJobsPerUser', data_type='int') # get rid of this form
    ])