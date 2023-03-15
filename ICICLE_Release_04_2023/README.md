## ICICLE_Release_04_2023

In this project we developed authenticated connections to kubernetes pods hosted on a TACC server. These clients include:

* Jupyter Notebooks 
* Command Line Interfaces

The Notebooks and the CLIs each have their own directory which is seen above.

The primary goals of our work were:

* Authenticate users using TACC accounts
* Create Neo4j Pods to be able to store data on Tacc Servers
* Load pre existing data into the Neo4j Pods
* Be able to set permissions of Pods
* Be able to parse Cypher queries from our clients and directly communicate with the data on our Pods
* Visualize data through neo4jupyter (notebooks)
* Have interactive user interface for requesting Cypher input (CLIs)


