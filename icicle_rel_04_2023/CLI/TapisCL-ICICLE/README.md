# TapisCLI
## Overview
Tapis CLI is designed to provide a simple to use, versatile way to interface with Tapis services hosted on HPC resources. User can either start the app and use it as a traditional command line applications, or pass commands directly from bash.
Allows you to work with all major Tapis services: Pods, Systems, Files, and Apps in one place. It can also interface directly with services being hosted on Tapis pods, like Neo4j. Although currently Neo4j is the only 3rd party application it can work with, adding support for Postgres and the like will not be difficult.

### Dependencies
* Dependencies are listed [here](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_04_2023/CLI/TapisCL-ICICLE/requirements.txt)

### Installation
#### Using PyPi
1. `pip install TapisCL-ICICLE`
2. `python -m TapisCL-ICICLE`
#### Running Python Code Directly
1. Clone the repository to local machine.
2. `python -m pip install -r requirements.txt`
3. `python cli.py`
### Operations
1. to see a list of all commands and their parameters, just enter help
