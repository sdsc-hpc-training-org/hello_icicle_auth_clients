import os
import sys


class Alias:
    def __init__(self):
        if 'win' in sys.platform:
            self.plat = 'win'
        else:
            self.plat = 'unix'
    
    def create_alias(self):
        if self.plat == 'win':
            print("windows")
            os.system(r"DOSKEY Tapiconsole=python C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\client-server\cli.py")
        else:
            os.system(r"alias Tapiconsole='python C:\Users\ahuma\Desktop\Programming\python_programs\REHS2022\Final-Project\Final-project-notebooks\TapisCLI\client-server\cli.py")

    def install_packages(self):
        os.system(r"pip install -r requirements.txt")

    def main(self):
        self.create_alias()
        self.install_packages()


if __name__ == "__main__":
    alias = Alias()
    alias.main()

