# ICICONSOLE

## Overview

ICICONSOLE is designed to provide an efficient and powerful interface to Neo4j Knowledge Graph databases hosted on HPC resources, leveraging Tapis. 

This application is specialized for knowledge graph querying, and has some basic CYPHER commands built in. 

### Dependencies
 
* Dependencies are listed [here](https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients/blob/main/icicle_rel_03_2023/CLI/ICICONSOLE/requirements.txt)

### Installation

Right now, the only way to use this application is to directly run the python code. 

```shell 
git clone https://github.com/sdsc-hpc-training-org/hello_icicle_auth_clients.git
```

```shell
cd hello_icicle_auth_clients/icicle_rel_03_2023/CLI/ICICONSOLE
```

```shell
python -m pip install -r requirements.txt
```

```shell
python ICICONSOLE.py
```

### First time user guide

You will be asked to login with your TACC account. If you aren't sure if you have this, visit the TACC [portal](https://portal.tacc.utexas.edu/).

Next, you will see the Tapis Pods that you have been given permission to access. If you don't see any, please contact the owner of the Pod you wish to access. Type in the ID of the Pod that you want to access. 

Once you do this, you will be in a custom made console for interfacing with the Knowledge Graph, using the Cypher language. If you know Cypher, you can start typing in commands like 

```
MATCH(n) RETURN n LIMIT 10
```

If you are not familiar with Cypher, don't worry! This is meant for users who have never used Cypher before. Type in "help" to view some of the built in commands to start exploring the knowledge graph. These built in commands will grow more extensive as time goes on. 

The welcome message for the Knowledge Graph console contains helpful tips, like "new", "exit", "clear", and "help". 
