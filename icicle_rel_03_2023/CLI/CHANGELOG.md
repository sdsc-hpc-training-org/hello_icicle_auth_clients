# Changelog
## TapisCLICICLE
### 0.0.60
#### 6/15/23
##### Changes
1. added Tapis federated authentication, and device code authentication grant types to allow for more flexible access to Tapis resources. Full revamp of the whole authentication workflow to achieve this
2. overhaul of user interface and command entry to provide better interactivity with commands that previously required config files to execute properly
3. More effective command line argument validation to sanitize data input
4. overhaul of files and systems to grant user access to additional tapis resources (WIP). Files and systems strive to emulate linux bash command line, using commands like cd and ls.
5. support for tapis postits added

##### Planned Changes
1. finish upgrading system authentication to fully complete system access
2. upgrade app commands and eventually implement intuitive job submission
3. refactor help generation code

## ICICONSOLE
### 0.0.10
#### 6/15/23
##### Changes
1. improved user interface for select queries. Now, the user can select a query from a list of available queries (help command), and the query will be executed automatically. This works toward an automated process for querying Knowledge Graphs.
2. for Knowledge Graph queries that return entire node(s), a separate view will be opened to display the node in a more readable format. In this view, scrolling is enabled to see the complete data in the confined space of the terminal.
3. minor bug fixes

##### Planned Changes
1. add support for Knowledge Graph queries that return edges
2. add automation for creation and deletion within Knowledge Graphs, past read-only operations.
3. integrate Tapis federated authentication
4. create a natural language interface for querying Knowledge Graphs, which would automate the automation process itself. This would be a long-term goal, and would require a lot of research and development.
