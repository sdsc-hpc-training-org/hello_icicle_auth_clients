class Formatters:
    """
    Format received dictionaries in the client code
    """
    def recursive_dict_print(self, input_data: dict, depth: int=0):
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
        if depth in (1, 0):
            print("\n")

    def print_response(self, response_message):
        """
        format response messages from the server
        """
        if type(response_message) == dict:
            self.recursive_dict_print(response_message)
        elif (type(response_message) == list or 
             type(response_message) == tuple or 
             type(response_message) == set):
            for value in response_message:
                self.print_response(value)
        else:
            print(response_message)