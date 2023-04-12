class Args:
    argparser_args = \
    {
        "command":{
            "args":["-c", "--command"],
            "kwargs":{"action":"store"}
        },
        "id":{
            "args":["-i", "--id"],
            "kwargs":{"action":"store"}
        },
        "template":{
            "args":["-t", "--template"],
            "kwargs":{"action":"store"}
        },
        "username":{
            "args":["-u", "--username"],
            "kwargs":{"action":"store"}
        },
        "level":{
            "args":["-L", "--level"],
            "kwargs":{"action":"store"}
        },
        "version":{
            "args":["-V", "--version"],
            "kwargs":{"action":"store"}
        },
        "file":{
            "args":["-F", "--file"],
            "kwargs":{"action":"store"}
        },
        "name":{
            "args":["-n", "--name"],
            "kwargs":{"action":"store"}
        },
        "uuid":{
            "args":["-U", "--uuid"],
            "kwargs":{"action":"store"}
        },
        "description":{
            "args":["-d", "--description"],
            "kwargs":{"action":"store"}
        },
        "verbose":{
            "args":["-v", "--verbose"],
            "kwargs":{"action":"store_true"}
        },
    }