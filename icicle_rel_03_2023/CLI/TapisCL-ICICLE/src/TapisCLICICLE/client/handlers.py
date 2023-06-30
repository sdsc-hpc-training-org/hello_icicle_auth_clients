from getpass import getpass
import os
import json

from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit import prompt
from blessed import Terminal

if __name__ != "__main__":
    from ..socketopts import schemas


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(f"{__file__}")))
saved_command = os.path.join(__location__, r'entered_command.json')


class Formatters:
    """
    Format received dictionaries in the client code
    """
    def print_response(self, input_data, depth: int=0):
        if isinstance(input_data, (list, set, tuple)):
            for data in input_data:
                if isinstance(data, (list, dict, set, tuple)):
                    print("\n")
                self.print_response(data, depth=depth+1)
        elif isinstance(input_data, dict):
            for name, data in input_data.items():
                if isinstance(data, (int, str)):
                    print(("  " * depth) + f"{name}: {data}")
                    continue
                print(("  " * depth) + f"{name}: ")
                self.print_response(data, depth=depth+1)
        elif isinstance(input_data, (int, str)):
            print(input_data)
        if depth == 0:
            print("\n")


class ParserTypeLenEnforcer:
        def __init__(self, name: str=str(), size: tuple=(0, 0), data_type: str='string', choices: list=list()):
            self.arg_name = name
            self.data_type = data_type
            self.lower_size_limit, self.upper_size_limit = size
            self.choices = choices

        def update_constraints(self, name=None, data_type=None, choices=None, size_limit=None, **kwargs):
            self.arg_name = name
            self.data_type = data_type
            self.choices = choices
            self.lower_size_limit, self.upper_size_limit = size_limit

        def __call__(self, data):
            if self.data_type:
                try:
                    if self.data_type == 'string':
                        str(data)
                    elif self.data_type == 'int':
                        int(data)
                except Exception as e:
                    raise ValidationError(message=str(e) + self.data_type, cursor_position=0)
            if self.data_type == int:
                if not data >= self.lower_size_limit or not data < self.upper_size_limit:
                    raise ValidationError(message=f"The input for the argument {self.arg_name} must be in the range ({self.lower_size_limit}, {self.upper_size_limit}). Got value {data}", cursor_position=0)
            elif self.data_type == str:
                if not len(data) >= self.lower_size_limit or not len(data) < self.upper_size_limit:
                    raise ValidationError(message=f"The input length for the argument {self.arg_name} must be in the range ({self.lower_size_limit}, {self.upper_size_limit}). Got length {len(data)}", cursor_position=0)
            if self.choices and data not in self.choices:
                raise ValidationError(message=f"The input for the argument {self.arg_name} must be one of the following: {self.choices}", cursor_position=0)


class ResponseValidator(Validator):
    def __init__(self):
        super().__init__()
        self.enforcer = ParserTypeLenEnforcer()

    def validate(self, document):
        text = document.text
        self.enforcer(text)
            

class Handlers(Formatters):
    def __init__(self):
        self.validator = ResponseValidator()

    def __expression_input(self) -> str: 
        """
        Input an expression as requested by the server for something like cypher queries
        """
        print("Enter 'exit' to submit") 
        expression = ''
        line = ''
        while line != 'exit': 
            line = str(input("> "))
            if line != 'exit':
                expression += line
        return expression
    
    def confirmation_handler(self, argument):
        if argument['description']:
            print(argument['description'])
        else:
            print("are you sure?")
        while True:
            decision = str(input("(y/n)"))
            if decision == 'y':
                decision = True
                break
            elif decision == 'n':
                decision = False
                break
            else:
                print("Enter valid response")
        return decision
    
    def form_handler(self, form_request: dict, term: Terminal):
        response = dict()
        repeat = True
        for field, attrs in form_request.items():
            while True:
                arg_type = attrs['arg_type']
                self.validator.enforcer.update_constraints(**attrs)
                try:
                    match arg_type:
                        case 'secure':
                            answer = prompt(f"{attrs['name']}: ", validator=self.validator, is_password=True)
                        case 'expression':
                            with term.fullscreen():
                                print(f"Enter expression input for the {attrs['name']} argument.")
                                answer = self.__expression_input()
                        case 'form':
                            answer, repeat = self.form_handler(attrs['arguments_list'], term)
                            print(f"ANSWER: {answer}")
                        case 'input_list':
                            repeat = True
                            answer = []
                            with term.fullscreen():
                                print(f"You are now entering data for {attrs['name']}")
                                while repeat:
                                    presentable_dict = {str(index+1):value for index, value in enumerate(answer)}
                                    print(f"{term.clear}reserved names: exit (enter these for special action). Enter index of an existing variable name to delete it\n{presentable_dict}")
                                    sub_answer, repeat = self.form_handler({str(len(answer)+1):attrs['data_type']}, term)
                                    index, value = list(sub_answer.items())[0]
                                    if value in presentable_dict:
                                        answer.pop(int(value)-1)
                                    elif value.lower() == 'exit':
                                        break
                                    else:
                                        answer.append(value)
                        case 'input_dict':
                            repeat = True
                            mode = 'create'
                            answer = dict()
                            default_name = attrs['data_type']['name']
                            with term.fullscreen():
                                print(f"You are now entering data for {attrs['name']}")
                                while repeat:
                                    print(f"{term.clear}reserved names: create, delete, exit (enter these for special action)\n{answer}\nmode: {mode}")
                                    attrs['data_type']['name'] = default_name
                                    name = str(input(f"enter the name for the instance of your {attrs['data_type']['name']}: "))
                                    if name.lower() in ('delete', 'create'):
                                        mode = name
                                        continue
                                    if name.lower() == 'exit':
                                        break
                                    if mode == 'create':
                                        mode = 'create'
                                        attrs['data_type']['name'] = name
                                        sub_answer, repeat = self.form_handler({name:attrs['data_type']}, term)
                                        answer.update(**sub_answer)
                                    elif mode == 'delete':
                                        mode = 'delete'
                                        try:
                                            answer.pop(name)
                                        except KeyError:
                                            pass
                        case 'str_input':
                            if 'description' in attrs and attrs['description']:
                                print(attrs['description'])
                            answer = prompt(f"{attrs['name']}: ", validator=self.validator)
                        case 'confirmation':
                            answer = self.confirmation_handler(attrs)
                        case 'silent':
                            continue
                        case _:
                            raise AttributeError(f"There is not argument type {arg_type}")
                    response[field] = answer
                    break
                except KeyboardInterrupt:
                    raise RuntimeError('Form cancelled, command execution stopped')
                except Exception as e:
                    with open(saved_command, 'w') as f:
                        f.write(json.dumps(response))
                        print(f"Argument input failure, command data written to file {saved_command}")
                        raise e
        return response, repeat
    
    def universal_message_handler(self, message: schemas.BaseSchema, term: Terminal):
        self.print_response(message.message)
        if message.error:
            self.print_response(message.error)
        if message.request_content:
            filled_form, repeat = self.form_handler(message.request_content, term)
            return filled_form, repeat
        return None, None
        
    def environment_cli_response_stream_handler(self, response):
        if response.schema_type == 'ResponseData' and response.exit_status: # if the command was a shutdown or exit, close the program
            self.print_response(response.response_message)
            os._exit(0)
        elif response.schema_type == 'ResponseData':
            if response.active_username:
                self.username = response.active_username
            if response.url:
                self.url = response.url
            self.print_response(response.response_message)