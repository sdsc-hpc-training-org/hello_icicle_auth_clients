# Hello Icicle Authentication Clients Software Release Notes:

**Secure Notebooks for Accessing Tapis PODs**

**Software release:** icicle_rel_03_2023

**Date:** 04/14/2023

## Notebook Overview
These notebooks are used as [templates](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/tree/main/icicle_rel_03_2023/Notebooks/TapisAuthTemplate) for developing Tapis authenticated applications, or as [demonstrators/examples](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/tree/main/icicle_rel_03_2023/Notebooks/ExampleApplications) of what you can do with Tapis in your applications.

### [TapisAuthTemplate](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_03_2023/Notebooks/TapisAuthTemplate/tapis_pods_auth.ipynb)
This notebook provides an extensible, easy to use base to build out a Tapis authenticated application. It comes with the Tapis auth included, and allows the user to add code to interface with Tapis without having to worry about the authorization.

**requirements:** [here](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_03_2023/Notebooks/TapisAuthTemplate/requirements.txt)

*these apply to the other applications below as well*

### Example Notebooks
Demonstrators of possible Tapis use cases
#### Pods
These notebooks are demonstrators for the Tapis pods service, for now focusing on Neo4j pods which can host knowledge graphs. They also demonstrate usage of the extensible Tapis Auth notebook.

##### **[load_data](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_03_2023/Notebooks/ExampleApplications/Neo4j/load_data.ipynb)**

Demonstrates several methods of loading data from CSV files into a Neo4j knowledge graph, through Tapis.

##### **[PPod](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_03_2023/Notebooks/ExampleApplications/Neo4j/PPod.ipynb)**

Demonstrates querying of a Neo4j knowledge graph pod hosting the ICICLE PPod ontology.


##### **[query_neo4j_architecture](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_03_2023/Notebooks/ExampleApplications/Neo4j/query_neo4j_architecture.ipynb)**

Demonstrates querying of a Neo4j knowledge graph pod hosting the Tapis architecture diagram

