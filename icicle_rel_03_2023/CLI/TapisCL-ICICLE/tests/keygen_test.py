import os


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

local_files = os.listdir(__location__)
if "id_rsa" not in local_files or "id_rsa.pub" not in local_files:
    os.system(f'ssh-keygen -q -m PEM -f {__location__}\\id_rsa -N ""')
    with open(f"{__location__}\\id_rsa", 'r') as f:
        formatted_key = ""
        for line in f.readlines()[1:-1]:
            formatted_key += line.strip()

    with open(f"{__location__}\\id_rsa", 'w') as f:
        f.write(formatted_key)

