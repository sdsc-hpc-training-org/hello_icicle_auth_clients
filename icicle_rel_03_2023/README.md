# Hello ICICLE Authentication Clients Software Release Notes:

**Software release:**  icicle_rel_03_2023

**Date:** 04/14/2023
<hr>

For this software release, we focussed on developing authenticated connections to kubernetes pods hosted on a TACC server (URL???). 
The primary goals of these applications included:

* Authenticating users using TACC accounts
* Creating Neo4j Pods to be able to store data on Tacc Servers
* Loading pre-existing data into the Neo4j Pods
* Setting permissions of Pods
* Parsing Cypher queries from our clients and directly communicate with the data on our Pods
* Visualizing data through neo4jupyter (notebooks)
* Developing an interactive user interface for requesting Cypher input (CLIs)

### icicle_rel_03_2023

For this software release, we focussed on developing authenticated connections to kubernetes pods hosted on any Tapis service. These applciations are stand-alone and can be installed separately. For details, see:

* [Jupyter Notebooks](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/tree/main/icicle_rel_03_2023)
   * [TapisAuth](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/tree/main/icicle_rel_03_2023/Notebooks/TapisAuth)
   * [Example Applications](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/tree/main/icicle_rel_03_2023/Notebooks/ExampleApplications)
* [Command Line Interfaces](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/tree/main/icicle_rel_03_2023/Notebooks)
   * [ICICONSOLE](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/tree/main/icicle_rel_03_2023/CLI/ICICONSOLE)
   * [TapisCL-ICICLE](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/tree/main/icicle_rel_03_2023/CLI/TapisCL-ICICLE)

The Notebooks and the CLIs each have their own directory and software requirements which are described here: 
