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