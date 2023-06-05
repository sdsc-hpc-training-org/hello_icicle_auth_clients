class Args: # should add a way to automatically check for duplicate entries to this class
    """
    specifies the set of arguments for the argparser in the CLI.py file. Putting them in here allows the helpers.py file to access these options, and generate help menus
    """
    argparser_args = \
    {
        "id":{
            "args":["-i", "--id"],
            "kwargs":{"action":"store"}
        },
        "template":{
            "args":["-t", "--template"],
            "kwargs":{
                "action":"store",
                "choices":[
                    "neo4j",
                    "postgres"
                ]}
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
        "destination_file":{
            "args":["-dF", "--destination_file"],
            "kwargs":{"action":"store"}
        },
        "source_file":{
            "args":["-sF", "--source_file"],
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
        "auth":{
            "args":["-a", "--auth"],
            "kwargs":{
                "action":"store",
                "choices":[
                    "password", 
                    "device_code", 
                    "federated"
                    ]
                }
        },
        "verbose":{
            "args":["-v", "--verbose"],
            "kwargs":{"action":"store_true"}
        },
        "help":{
            "args":['-h', '--help'],
            "kwargs":{"action":"store_true"}
        }
    }

    @staticmethod
    def check_duplicates():
        keys = []
        arguments = []
        for key, value in Args.argparser_args.items():
            if key in keys:
                raise AttributeError(f"Duplicate argument name {key} found in args")
            elif any(param in value['args'] for arg_list in arguments for param in arg_list): # horrific function I asked chatgpt to make because nested for loops are bad :(
                raise AttributeError(f"Duplicate command line parameter {value} foudn in args")
            keys.append(key)
            arguments.append(value)
            

if __name__ != "__main__":
    Args.check_duplicates
