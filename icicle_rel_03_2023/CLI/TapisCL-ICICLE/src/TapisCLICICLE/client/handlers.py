from getpass import getpass
import os


if __name__ != "__main__":
    from ..socketopts import schemas


class Handlers:
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
                    response[field] = None
                response[field] = answer
        return response
    
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