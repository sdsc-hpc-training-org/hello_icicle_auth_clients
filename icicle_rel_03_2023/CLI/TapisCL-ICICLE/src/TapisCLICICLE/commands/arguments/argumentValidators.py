def cast_int(data):
    return int(data)

def cast_string(data):
    return str(data)

def cast_bool(data):
    return bool(data)



class Validators:
    type_map = {
        'int':cast_int,
        'string':cast_string,
        'bool':cast_bool
    }
    def __init__(self, arg_type):
        self.validator_map = {
            'silent':self.no_validator,
            'secure':self.standard_validator,
            'expression':self.standard_validator,
            'str_input':self.standard_validator,
            'standard':self.standard_validator,
            'confirmation':self.confirmation_validator,
            'input_list':self.list_validator,
            'input_dict':self.dict_validator,
            'form':self.form_validator,
            'selection_list':self.selection_list_validator
        }

    def set_default_if_needed(self, value):
        """
        if there is no value, set the default value. If the value is False, return False
        """
        if value == None and self.default_value:
            value = self.default_value
            return (True, value)
        elif not value:
            return (True, value)
        return (False, value)
    
    def check_data_type_followed(self, value):
        """
        check if the value is of the correct datatype
        """
        try:
            return self.type_map[self.data_type](value)
        except:
            raise ValueError(f"The argument {self.argument} requires a datatype {self.data_type}")
        
    def check_size_limit_followed(self, value):
        """
        check that the value abids byt he size limit
        """
        min_, max_ = self.size_limit
        if min_ != -1 and max_ != -1:
            if type(value) == int:
                if value >= max_ or value < min_:
                    raise ValueError(f"The argument {self.argument} must be a value in the range {self.size_limit}")
            elif type(value) == str and (len(value) >= max_ or len(value) < min_):
                raise ValueError(f"The argument {self.argument} must be between the sizes {self.size_limit}")

    def no_validator(self, value):
        return value
    
    def standard_validator(self, value):
        """
        check to make sure the value assigned to the argument follows all existing rules
        """
        return_default, value = self.set_default_if_needed(value)
        if return_default:
            return value
        value = self.check_data_type_followed(value)
        self.check_size_limit_followed(value)
        if self.choices and value not in self.choices:
            raise ValueError(f"The value for argument {self.argument} must be in the list {self.choices}")
        if self.arg_type != 'bool' and isinstance(value, bool):
            return None
        return value
    
    def confirmation_validator(self, value):
        if self.required and not value:
            raise RuntimeError("Declined confirmation, cancelling")
        return value
    
    def list_validator(self, value):
        if value and not isinstance(value, bool):
            processed_values = list()
            for sub_value in value:
                processed_values.append(self.data_type.verify_rules_followed(sub_value))
            return processed_values
        if isinstance(value, bool) and value:
            return True
        else:
            return None
    
    def dict_validator(self, value):
        if value and not isinstance(value, bool):
            print(f"DICT VALUE {value}")
            processed_values = dict()
            for sub_name, sub_value in value.items():
                processed_values[sub_name] = self.data_type.verify_rules_followed(sub_value)
            return processed_values
        if isinstance(value, bool) and value:
            return True
        else:
            return None
    
    def form_validator(self, value):
        if value and not isinstance(value, bool):
            flattened_value = self.flatten_form_data(value)
            results = dict()
            for argument_name, argument in self.arguments_list.items():
                results[argument_name] = argument.verify_rules_followed(flattened_value[argument_name])
            return flattened_value
        if isinstance(value, bool) and value:
            return True
        else:
            return None
    
    def selection_list_validator(self, value):
        if value and not isinstance(value, bool):
            results = dict()
            for field, field_bool in value.items():
                if field_bool:
                    results[field] = self.option_dict[field]
        else:
            return None
        return results

        
