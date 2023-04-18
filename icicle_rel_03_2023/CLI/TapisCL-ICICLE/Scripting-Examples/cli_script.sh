#! /bin/bash
# example bash program shows how you can add someone as admin to all accessible pods. You can make bash scripts with TapisCLICICLE, if you want

output=$(python -m TapisCLICICLE pods -c get_pods)

pod_ids=($(echo "$output" | grep -oP '(?<=Pod ID: ).*'))
# Print the output
for pod_id in "${pod_ids[@]}"
do
    python -m TapisCLICICLE pods -c set_pod_perms -i <user> -L admin
done

echo $output