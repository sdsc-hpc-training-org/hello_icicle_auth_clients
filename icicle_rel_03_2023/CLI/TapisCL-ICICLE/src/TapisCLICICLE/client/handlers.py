from getpass import getpass
import os

from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit import prompt

if __name__ != "__main__":
    from ..socketopts import schemas


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
        type_map = {'int':int, 'string':str}
        def __init__(self, name: str=str(), size: tuple=tuple(), data_type: str=str(), choices: list=list()):
            self.arg_name = name
            self.data_type = self.type_map[data_type]
            self.lower_size_limit, self.upper_size_limit = size
            self.choices = choices

        def __call__(self, data):
            try:
                self.data_type(data)
            except:
                raise ValidationError(f"The input for the argument {self.arg_name} must be of type {self.data_type}. Got type {type(data)}")
            if self.data_type == int:
                if not data >= self.lower_size_limit or not data < self.upper_size_limit:
                    raise ValidationError(f"The input for the argument {self.arg_name} must be in the range ({self.lower_size_limit}, {self.upper_size_limit}). Got value {data}")
            if not len(data) >= self.lower_size_limit or not len(data) < self.upper_size_limit:
                raise ValidationError(f"The input length for the argument {self.arg_name} must be in the range ({self.lower_size_limit}, {self.upper_size_limit}). Got length {len(data)}")
            if self.choices and data not in self.choices:
                raise ValidationError(f"The input for the argument {self.arg_name} must be one of the following: {self.choices}")


class ResponseValidator(Validator, ParserTypeLenEnforcer):
    def __init__(self):
        super().__init__()

    def update_constraints(self, arg_name=None, data_type=None, choices=None, size_limit=None, **kwargs):
        self.arg_name = arg_name
        self.data_type = data_type
        self.choices = choices
        self.size_limit = size_limit

    def validate(self, document):
        text = document.text
        self(text)
            

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
    
    def confirmation_handler(self):
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
    
    def form_handler(self, form_request: dict):
        response = dict()
        repeat = False
        for field, attrs in form_request.items():
            while True:
                arg_type = attrs['arg_type']
                self.validator.update_constraints(**attrs)
                match arg_type:
                    case 'secure':
                        answer = prompt(attrs['argument'], validator=self.validator(), is_password=True)
                    case 'expression':
                        answer = self.__expression_input()
                    case 'form':
                        answer = self.form_handler(attrs['arguments_list'])
                    case 'input_list':
                        repeat = True
                        answer = []
                        while repeat:
                            sub_answer, repeat = self.form_handler(attrs['data_type'])
                            answer.append(sub_answer)
                    case 'input_dict':
                        repeat = True
                        answer = dict()
                        while repeat:
                            name = str(input(f"enter the {attrs['data_type']['argument']} for the instance of {attrs['argument']}"))
                            sub_answer, repeat = self.form_handler(attrs['data_type'])
                            answer[name] = sub_answer
                    
                # try:
                #     if field not in ("expression", "confirmation", "password", "user_code"):
                #         answer = str(input(f"{field}: "))
                #     elif field == "expression":
                #         answer = self.__expression_input()
                #     elif field == "confirmation":
                #         answer = self.confirmation_handler()
                #     else:
                #         answer = getpass("password: ")
                #     if not answer:
                #         answer = None
                # except KeyboardInterrupt:
                #     continue
                response[field] = answer
                break
        return response, repeat
    
    def universal_message_handler(self, message: schemas.BaseSchema):
        self.print_response(message.message)
        if message.error:
            self.print_response(message.error)
        if message.request_content:
            filled_form = self.form_handler(message.request_content)
            return filled_form
        return None
        
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