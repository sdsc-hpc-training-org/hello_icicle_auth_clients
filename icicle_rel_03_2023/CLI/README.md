# Hello Icicle Authentication Clients Software Release Notes:
## Command Line Interface applications 
**Software release:** icicle_rel_03_2023

**Date:** 04/14/2023

## Overview
These two command line applications provide a user friendly way to access and manage Tapis services. 

### General Requirements
1. An account and login credentials for a Tapis service running on HPC system (TACC or Expanse for instance)
2. A python installation

### TapisCL-ICICLE
**Functions:**
* Command line interface to manage and operate Tapis services
 * Pods
 * Services
 * Files
 * Apps/Jobs

**Dependencies:** [here](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_03_2023/CLI/TapisCL-ICICLE/requirements.txt)

**Installation Options:** 
1. As PyPi package
2. Directly from github

[see here for installation instructions](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_03_2023/CLI/TapisCL-ICICLE/README.md)

### ICICONSOLE
**Functions:**
* Command line interface specifically aimed toward working with Neo4j hosted on Tapis pods.
 * Direct entry of cypher commands into the console to be executed by Neo4j
 * Also provides python library which wraps over Cypher commands
 
**Dependencies:** [here](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_03_2023/CLI/ICICONSOLE/requirements.txt)

**Installation Options:** 
1. As PyPi package
2. Directly from github

[see here for installation instructions](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_03_2023/CLI/ICICONSOLE/README.md)
