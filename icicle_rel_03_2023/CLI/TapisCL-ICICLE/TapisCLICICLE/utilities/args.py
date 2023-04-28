class Args:
    """
    specifies the set of arguments for the argparser in the CLI.py file. Putting them in here allows the helpers.py file to access these options, and generate help menus
    """
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
        "link":{
            "args":["-l", "--link"],
            "kwargs":{"action":"store"}
        },
        "verbose":{
            "args":["-v", "--verbose"],
            "kwargs":{"action":"store_true"}
        },
    }