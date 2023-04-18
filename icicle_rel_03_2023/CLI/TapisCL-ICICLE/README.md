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
2. `python -m TapisCLICICLE`
#### Running Python Code Directly
1. Clone the repository to local machine.
2. `python -m pip install -r requirements.txt`
3. `python cli.py`
### Operations
**Full Terminal Interface:**
1. run ``python -m TapisCLICICLE``
2. You will be promted to enter a Tapis service link. You can find this on the Tapis service provider's wesbite usually. If you are working with icicle, this should be https://icicle.tapis.io
3. enter your username and password when prompted
4. if all went well the console should open. You can run `help` to see command options
5. to exit the application, run `exit`

**Command Line:**

Alternatively, if you do not want to enter the actual command line environment of the TapisCL-ICICLE application, you can run commands directly from the command line like this:

`python -m TapisCLICICLE pods -c help`

this may still ask you for authentication, however once you are logged in once, you do not need to enter your credentials again unless the 5 minute timeout period passes, in which case the application shuts itself off.

**Scripting**

Python and Bash scripting examples are available [here](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/tree/main/icicle_rel_03_2023/CLI/TapisCL-ICICLE/Scripting-Examples)

