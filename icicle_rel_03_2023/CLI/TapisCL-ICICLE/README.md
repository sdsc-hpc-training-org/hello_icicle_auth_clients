# TapisCLI
Please remember to create an issue in this repository if you encounter any bugs, we will do our best to fix it quick!
## Overview
Tapis CLI is designed to provide a simple to use, versatile way to interface with Tapis services hosted on HPC resources. User can either start the app and use it as a traditional command line applications, or pass commands directly from bash.
Allows you to work with all major Tapis services: Pods, Systems, Files, and Apps in one place. It can also interface directly with services being hosted on Tapis pods, like Neo4j. Although currently Neo4j is the only 3rd party application it can work with, adding support for Postgres and the like will not be difficult.

### Dependencies
* Dependencies are listed [here](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_03_2023/CLI/TapisCL-ICICLE/requirements.txt)

### Installation
#### Using PyPi
1. `pip install TapisCL-ICICLE`. Current version 0.0.24
2. run using `python -m TapisCLICICLE`
#### Running Python Code Directly
1. Clone the repository to local machine.
2. `python -m pip install -r requirements.txt`
3. from the src folder, run using `python -m TapisCLICICLE`

### Known Issues
Since the application relies heavily on sockets to run properly, when they fail so does the application. If the application crashes frequently, or doesnt start, you should restart your computer, this should fix the issue. If it doesnt however, check the logs.log file, and create an issue on the github repo.
The application has known compatibility issues with the WSL vpn due to its reliance on sockets. If you intend to use the application with WSL turn off your VPN. If the application doesnt work and you have a VPN on, turn it off just to make sure.

## Usage
### Interfaces
TapisCLICICLE supports two interface types:
#### Full Terminal Interface:
If you want a full fledged command line environment to interact with your Tapis services, run the app using `python -m TapisCLICICLE` with no additional arguments. This will spawn the environment where you can enter commands.
#### Bash Command Line:
Alternatively, if you want to enter commands directly into your bash terminal, you can run the app with arguments. For example, `python -m TapisCLICICLE create_pod (pod_name) (pod_template)` will create a pod without opening the app environment. The same goes for all commands.

### Authentication
TapisCLICICLE supports 3 authentication methods, password, federated, and device code grants. Authentication has a timeout of 5000 seconds of inactivity.
For each method of authentication, you will be asked to submit a tenant URI. This determines what resources you will have access to. 
For both federated and device code grants, you will be prompted to create a session password for secure operations (like obtaining pod credentials)
#### Password
You can log in to the app using an account username and password for the TACC portal. You must obtain an account directly from TACC to use this login method.

#### Federated
Requires a valid CILogon account through your university, with google, or with ORCID. Upon selecting this method, a webpage will open requesting login with one of these methods. Once you are authenticated you will receive an access token on the webpage. Dont show this token to anyone. Simultaneously you will be prompted to enter this token on the TapisCLICICLE app. Once you do, you will be authenticated and can use the app.

#### Device Code
This is functionally the same as the federated authentication, except you are prompted to enter an app generated user code to generate your token after logging in using CILogon. Once you generate your token you must confirm completion on the app and you will be authenticated

#### Notes on Authentication
Both federated and device code grants are experiemental at the current state in development, and work on only a few tenants

### Help
TapisCLICICLE supports several Tapis services for interfacing with HPC systems. Basic information on these services can be obtained using the `help` command.
If you want to get a list of commands which fall under a certain service, enter the service name into the command line. For example, running `Systems` will show all commands under the systems service
To get information about an individual command, you can run `(command) -h`. This will list all command syntax. Running `(command) -h -v`, specifying verbose with -v will give detailed description of each argument associated with the command
When running help commands, arguments marked with an (f) do not receive values directly, but send a request for a form back to the client.

### Commands
Commands in TapisCLICICLE can be divided into 2 classifications: creational and managerial

#### General Commands
General commands are for managing and viewing information on your current application session.

General Commands:
* whoami: return information about the current logged in user
* whereami: return the current tenant URI
* switch_tenant_to --tenant_uri (tenant_uri) --auth (auth type): log in to a different tenant without shutting down the app. Tenant URI is the base URL of the tenant you want to connect to. For example, icicle.tapis.io, or smartfoods.tapis.io. The auth parameter must be one of the 3 authentication methods previously mentioned, password, federated, or device_code grant.
* exit: exit the current instance of the application client without deactivating the app entirely. The app continues to run in the background until timeout, or a new user session starts. Starting the client again after
* shutdown: completely shut down the application client and background. If you want to run the application again you will have to re-authenticate
* user (username): gets information about the user connected to the specified username
* get_tenants: gets a list of available tenants to connect to
* get_tenant (tenant_id): get more detailed information about a specific tenant specified by the tenant id.
* manpages: brings you to this page

#### Creational
These commands are for creating and updating Tapis services like pods and systems. These commands generally have lots of optional arguments for configuration, and forms to fill out. If you choose, in lieu of writing your configurations in the command line you can write and upload your own service config file from an application generated config file template. For all creational commands, you can do this by adding the argument `-f (path to your config file)`
In the event that you do make a mistake while writing your config in the command line, your work is saved to a config file (the application will tell you where when this happens). When you fix the errors in the config file you can immediately re-upload it to try again.

Creational commands include:
* create_system
* update_system
* create_pod
* update_pod
* create_volume
* update_volume
* create_snapshot
* update_snapshot
* create_app
* update_app
* submit_job
  
#### Managerial
Managerial commands are generally for getting information about the Tapis services you have access to, managing permissions, state, and sharing for those services. These wont usually have more than 3 arguments. 

### Services
Each Tapis service has their own command group which allows you to interface with that service. Currently, TapisCLICICLE supports 7 services:
* Systems
* Files
* Apps
* Jobs
* Pods
* Volumes
* Query

#### Systems
Systems lie at the core of most workflows in Tapis, and TapisCLICICLE. They are representations of your account on an HPC system, and interface with HPC resources using SSH. You can read more specifics about Tapis systems [here](https://tapis.readthedocs.io/en/latest/technical/systems.html). Systems enable the user to store and access files on as well as run jobs on that resource. 
Each system has 4 key characteristics:
* id: the identifier for the system
* systemType: What type of system are you interfacing with? LINUX, IRODS, or GLOBUS
* host: What is the hostname of the system you are trying to connect to? This can be anything that supports Tapis systems, whether it be a url or IP address. SOmething like stampede2.tacc.utexas.edu
* defaultAuthnMethod: What authentication method will you use on this system? 
  * LINUX: PASSWORD or PKI_KEYS
  * IRODS: PASSWORD
  * GLOBUS: TOKEN

##### Important System Fields
* canExec: If you want to execute jobs on your system, you will have to specify this flag and fill out the form
* canRunBatch: similar to canExec, if you want to run your jobs using a batch scheduler, you must specify this flag and fill out the batch form
* jobEnvVariables: Environment variables to be passed to job containers when theyre run on your system
* jobCapabilities: add descriptors and configurations to jobs by default
* jobConstraints: specify how many jobs can be run at once on a system, or by a user on that system
* rootDir: if you want to use your system for storage, this is the root directory from which file operations will be conducted on the system

##### S3 Bucket Systems
Tapis also supports interfacing with AWS S3 Bucket systems. These only support the Access key authentication method. Out of the fields mentioned previously, s3 bucket systems only support the canRunBatch field

##### Child Systems
You can create child systems which inherit all attributes from the parent on creation using the create_child_system command. These children can be unlinked later, and act as standalone systems

#### Files
File commands allow the user to interface with the file system of a select system. To a limited extent, for file system navigation, and basic file management, the application replicates the linux bash environment.

In order to 'enter' a system and its gain more direct access to its files, use the command `system (system_id)`. Although all the file commands have the option of specifying the system_id you are accessing the files of, entering the system using the system command makes this unecessary. You can then run commands like ls, as you would on a linux system

Files can only be accessed if you are authenticated to the system the files are on. If the system does not have a rootDir attribute, files will be inaccessible

you can read more about Tapis files [here](https://tapis.readthedocs.io/en/latest/technical/files.html)

##### File Permissions and Sharing
You have two options for permissions and sharing:
* permissions: the more traditional way, granting read or modify permissions to an individual for a file or path. This is governed by grant_permissions and delete_permissions in the app
* Postits: postits are a service for securely sharing individual file paths with large groups on a tenant or with individuals. These are interoperable between tenants as well. Postits are not persistent and die after a set period of time, and must be redeemed in order to access the files contained within. You can limit the number of times a postit can be redeemed, after which it will be deleted.

#### Apps
Apps are persistent representations of containers stored on a specific tenant. They require a systemId, for a system which has the canExec and canRunBatch flags set to true, and they are required for running jobs. The container for the job you want to run must be stored in an app. Using apps you can specify default job attributes, like environment variables or runtime characteristics. You can read more about Tapis applications [here](https://tapis.readthedocs.io/en/latest/technical/files.html).

Creating an app requires an app id, a version, container image (from docker or singularity hub), and the execSystemId (the default system on which jobs derived from this app will be executed). When creating an app, you can use the same app id as an already created app, as long as you specify a new version.

some important fields for app creation include:
* configureRuntime: specify runtime options, like the runtime type (singularity or docker), as well as runtime options (SINGULARITY_START, SINGULARITY_RUN, and or NONE)
* jobConstraints: place limits on how many jobs can be run, and specify if the job is batch or fork
* defaultSystemConfig: specify system id for running jobs, and system filepaths for input and output files
* appArgs: create a list of arguments that must be passed at runtime to the job for it to run
* containerArgs: create a list of arguments for configuring the job's container
* envVariables: create a list of environment variables to be passed to the job at runtime
* jobAllocationConfiguration: configure features of the app like nodeCount and memory allocation.

App permissions can be managed the same as files.

#### Jobs
The jobs service allows the execution of programs, 'jobs', on a system. A job must be derived from an app and run on a system with canExec (and often with canRunBatch) enabled.

Submitting a job only requires an appId and job name, provided default job characteristics were specified in the app's definition. You can specify, or override these settings by specifying them directly in the submit_job command. For important job submission fields, see the important fields for app creation. To manage a job, at job creation you will be given a job Uuid. Most Job commands require this Uuid. 

While a job is running you can use get_job to see it status and information. After it finishes you can see its history using get_job_history.

In order to share a job, you can use the share_job command. You can list who the job is being shared with using the get_job_share command, and delete sharing with delete_job_share

##### Job Subscriptions
If you want to be notified of certain events on a job via email or webhook, you can create a subscription to a job. You can do this with the subscribe_to_job command

#### Pods
Pods are a semi-persistent way of storing data or running servers on HPC. Pods are not system dependent, and are standalone. You can read more about Tapis pods [here](https://tapis.readthedocs.io/en/latest/technical/pods.html)

These are kubernetes pods running specific applications. What application is run on the pod depends on the 'template' field specified at creation time of the pod. Currently, the only publically available templates are neo4j and postgres, however you can run your own custom pod with approval from admin. If you want your own custom pod template, send a message in the Tapis slack server [here](http://bit.ly/join-tapis).

Creating a pod only requires a pod id and template. Other important fields include:
* volume_mounts: attach a kubernetes volume to backup data from pod to
* command: list of commands to be run in the pod at runtime
* environment_variables: environment variables for a custom pod
* time_to_stop_default/instance: specify how long the pod will live. If set to -1 the pod lives forever, until manually stopped. If a pod stops, the data is lost unless backed up!

##### Data Persistence for Pods
As mentioned, the data on pods is semi-persistent. You could set the pod to live forever and data will persist as long as it doesnt run into any errors. If you want true data persistence you will have to use the Volumes service. When creating a pod, you can specify a volume mount, which if the volume id doesnt exist will create a new one for you. Alternatively, you can create a volume yourself.

#### Volumes
The volumes service provides an interface to kubernetes volumes, which unlike pods are fully persistent. During pod configuration, you can backup certain directories in your pod to the volume, which will be loaded to the pod if it ever restarts. You can read more about Tapis volumes [here](https://tapis-project.github.io/live-docs/?service=Pods#tag/Volumes)

creating a volume only requires a volume id.

If you want to create a sort of archive for a volume to save data at a certain state, you can create a snapshot using the crate_snapshot command

#### Query
Query allows direct command line interfacing with pod hosted database services, currently only neo4j and postgres. All it requires is a pod id, and you will be able to send queries to either database service. For neo4j you can also use Sahil Samar's [here](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/tree/main/icicle_rel_03_2023/CLI/ICICONSOLE), which supports natural language parsing for neo4j

### Issues
As of right now, Im about to head off to college and wont have time to actively maintain TapisCL-ICICLE. Whether or not it gets picked up by another intern, im not sure. In any case, if you encounter an issue with app submit a bug report to [our github page](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/issues). I will do my best to fix it for you. I do not plan on adding any major new features in future.







