from getpass import getpass
import os


if __name__ != "__main__":
    from ..socketopts import schemas


class Formatters:
    """
    Format received dictionaries in the client code
    """
    def __recursive_dict_print(self, input_data: dict, depth: int=0):
        for key, value in input_data.items():
            if isinstance(value, dict):
                print(("  " * depth) + f"{key}:")
                self.recursive_dict_print(value, depth=depth + 1)
            elif isinstance(value, (list, tuple, set)):
                print(("  " * depth) + f"{key}:")
                for data in value:
                    print(("  " * (depth + 1)) + data)
            else: 
                print(("  " * depth) + f"{key}: {str(value).strip()}")
        if depth in (0,):
            print("\n")

    def print_response(self, response_message):
        """
        format response messages from the server
        """
        if type(response_message) == dict:
            self.__recursive_dict_print(response_message)
        elif type(response_message) in (set, tuple, list):
            for value in response_message:
                self.print_response(value)
        else:
            print(response_message)


class Handlers(Formatters):
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
        for field in form_request.keys():
            while True:
                try:
                    if "password" not in field:
                        answer = str(input(f"{field}: "))
                    elif field == "expression":
                        answer = self.__expression_input()
                    elif field == "confirmation":
                        answer = self.confirmation_handler()
                    else:
                        answer = getpass("password: ")
                    if not answer:
                        answer = None
                except KeyboardInterrupt:
                    continue
                response[field] = answer
                break
        return response
    
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