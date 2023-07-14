import json

import baseCommand
import arguments.argument as argument


class baseConfigGenerator(baseCommand.BaseCommand):
    required_arguments = [
        argument.SelectionList('appServiceOptions', option_dict={
            ''
        })
    ]