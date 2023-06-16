# purpose
One critical issue from day one of development was reconciling the need for simple, user friendly data entry, with the quantity and scope of data entry supported. Originally, the Tapis API was designed with config files in mind for the configuration of systems, pods, apps, etc. This is hardly convenient for someone who doesnt have experience (or just doesnt want to deal with) configuring files. Since in previous releases, function parameters were already turning into metadata (instead of preserving their original funciton as parameters), so new versions will implement the argument class to streamline the input of data by the client.

client should still be allowed to submit config files, however. If there is a command that support both config files and command line input, when the command line input is entered for config parameters it should write to a config file so that the information is saved (espeically in case of failure)

there must be a way for the argument to access tapis actor specific data for choices

## Frontend Operations:
### Arg types:
* secure: prompt client to enter using getpass
* expression: prompt multiline string input
* input_list: prompt user to enter data in format matching the datatype. After finishing the entry, clicking enter results in asking for another copy of the datatype. ctrl+c will exit if done in between
* input dict: same as input list, except user is also prompted to enter a key for the argument they are filling out
* form: user given a pre-selected set of fields to fill out
* str_input: one liner string input
* standard: regular CLI argument