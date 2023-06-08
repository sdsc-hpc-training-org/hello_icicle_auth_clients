desired_arguments = [
    'username',
    'usernam',
    'umbology',
    'Uggolino',
    'background',
    'Bungee',
    'zingo',
    'zonker',
    'output_file',
    'file']


def generate_truncated_argument(argument, truncated_arguments_list, attempt=1):
    if argument[attempt-1] in ('_', '-'):
        attempt += 1
    truncated_argument = argument[:attempt]
    if f"-{truncated_argument}" in truncated_arguments_list:
        return generate_truncated_argument(argument, truncated_arguments_list, attempt=attempt+1)
    return truncated_argument


def generate_arguments_list(desired_arguments):
    truncated_arguments = list()
    full_arguments = list()
    for desired_argument in desired_arguments:
        if f"--{desired_argument}" in full_arguments:
            raise ValueError(f"Duplicate argument name {desired_argument}")
        full_arguments.append(f"--{desired_argument}")
        truncated_argument = generate_truncated_argument(desired_argument, truncated_arguments)
        truncated_arguments.append(f"-{truncated_argument}")

    return list(zip(full_arguments, truncated_arguments))


print(generate_arguments_list(desired_arguments))
