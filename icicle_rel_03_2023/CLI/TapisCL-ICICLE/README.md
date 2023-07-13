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

##### Generating Config Files
WIP

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

##### S3 Bucket Systems
Tapis also supports interfacing with AWS S3 Bucket systems


