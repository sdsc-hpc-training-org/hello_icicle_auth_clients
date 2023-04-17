#! /bin/bash

output=$(python -m TapisCLICICLE pods -c get_pods)

# Print the output
echo $output