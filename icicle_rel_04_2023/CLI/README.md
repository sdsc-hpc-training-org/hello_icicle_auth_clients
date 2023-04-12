# Hello Icicle Authentication Clients Software Release Notes:
## Command Line Interface applications 
**Software release:**  icicle_rel_04_2023
**Date:** 04/14/2023
<hr>

## Secure Notebooks for Accessing Tapis PODs


## Description/Oveverview
Overview here

## Installation/Software Reqquirements
software requirements here

## Notebook Overview
about the notebooks, packagages, etc

### CLI App1 description
* what does the app do?
* packages

### CLI App2 description
* what does the app do?
* packages


<hr>
### MPT Notes:
* where they run from
* module dependencies



* Authenticates a user to Tacc
* Creates a Tapis pod with a Neo4j template
* Sets permissions for a Tapis pod
* Establishes a connection to the Pod via py2neo

## load_data.ipynb

* Shows how to load pre-existing CSV data into an empty Neo4j Tapis Pod







<hr>
<hr>
that we developed. (these will probably be combined later)

## ICICONSOLE

* Requires Tacc Authentication
* Allows for direct access to all Tapis Pods authorized to the signed in Tacc user
* Cypher console for Neo4j Pods
* Direct parsing of commands to cypher with basic display of results 
* includes python library that wraps simple cypher commands in python functions

## TapisCLI

* Requires Tacc Authentication
* Tapis service management
  * pods
  * services
  * files
  * apps
* command line interface for above services
* use as a full terminal application, or enter commands directly into the terminal window
* also interface with individual pods
  * enter commands for neo4j pods
* planning to add curses interface in the future
* I will make the pypi toml later
