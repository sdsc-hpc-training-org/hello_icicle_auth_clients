from getpass import getpass
import os


if __name__ != "__main__":
    from ..socketopts import schemas


class Handlers:
    def fillout_form(self, form: list) -> dict:
        """
        fill out a form as requested by the server for more complicated functions
        """
        filled_form = dict()
        for field in form:
            value = str(input(f"{field}: ")).strip()
            if not value:
                value = None
            filled_form.update({field:value})
        return filled_form
    
    def form_handler(self, response):
        if not response.arguments_list:
            form = self.expression_input()
            filled_form = schemas.FormResponse(arguments_list=form)
        else: 
            form = self.fillout_form(response.arguments_list)
            filled_form = schemas.FormResponse(arguments_list=form)
        return filled_form

    def auth_handler(self, response):
        if response.secure_input or not response.requires_username:
            username = self.username
            password = getpass("Password: ")
        else: 
            username = input("Username: ")
            password = getpass("Password: ")
        filled_form = schemas.AuthData(username=username, password=password)
        return filled_form
    
    def confirmation_handler(self, response):
        print(response.message)
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
        filled_form = schemas.ResponseData(response_message=decision)
        return filled_form
    
    def expression_input(self) -> str: 
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