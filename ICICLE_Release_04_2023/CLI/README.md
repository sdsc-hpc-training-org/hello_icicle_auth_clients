There are two Command Line Interface applications that we developed. (these will probably be combined later)

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