from commands import commandMap


if __name__ == "__main__":
    pods = commandMap.Pods()
    args = commandMap.ArgsGenerator().get_all_args(pods.command_map)
    for arg_name, arg in args.items():
        print(f"{arg_name}: {arg.truncated_arg}/{arg.full_arg}")