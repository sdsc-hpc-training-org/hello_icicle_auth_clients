import json


class tapisObject:
    def __init__(self, tapis_instance, username, password):
        self.t = tapis_instance
        self.username = username
        self.password = password
        self.help_path = r'C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\subsystems\help.json'

        with open(self.help_path, 'r') as h:
            json_help = h.read()
            self.help = json.loads(json_help)
