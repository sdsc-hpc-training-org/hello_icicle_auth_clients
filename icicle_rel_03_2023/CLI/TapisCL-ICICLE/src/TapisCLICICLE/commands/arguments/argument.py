import typing
import abc


ALLOWED_ARG_TYPES = typing.Literal['silent', 'secure', 'expression', 'input_list', 'input_dict', 'form', 'str_input', 'confirmation']
ALLOWED_DATA_TYPES = typing.Literal['string', 'int', 'bool']
ALLOWED_ACTIONS = typing.Literal['store', 'store_true', 'store_false']


class AbstractArgument(abc.ABC):
    @abc.abstractmethod
    def json(self):
        pass

def cast_int(data):
    return int(data)

def cast_string(data):
    return str(data)

def cast_bool(data):
    return bool(data)


class Argument(AbstractArgument):
    type_map = {
        'int':cast_int,
        'string':cast_string,
        'bool':cast_bool
    }
    def __init__(self, argument: str,
                 data_type: ALLOWED_DATA_TYPES | typing.Type[AbstractArgument] = 'string',
                 arg_type: ALLOWED_ARG_TYPES | typing.Literal['standard']='standard',
                 choices: list | None=None, 
                 action: typing.Literal['store', 'store_true', 'store_false']="store", 
                 description: str="",
                 positional: bool=False,
                 default_value=None,
                 depends_on: list = [],
                 mutually_exclusive_with: list = [],
                 size_limit: tuple=(0,4096)):
        if arg_type not in typing.get_args(ALLOWED_ARG_TYPES) and arg_type != 'standard':
            raise ValueError(f"The arg type parameter in the argument {self.__class__.__name__} must be in the list {ALLOWED_ARG_TYPES}. Got arg type {arg_type}")
        if data_type not in typing.get_args(ALLOWED_DATA_TYPES) and not issubclass(data_type.__class__, AbstractArgument):
            raise ValueError(f"The data type argument provided to the argument {self.__class__.__name__} must be in the list {ALLOWED_DATA_TYPES}, or must be a subclass of AbstractArgument")
        if action not in typing.get_args(ALLOWED_ACTIONS):
            raise ValueError(f"Action {action} not in the list {ALLOWED_ACTIONS}, in argument {self.__class__.__name__}")
        if arg_type in ('input_list', 'input_dict') and isinstance(data_type, Argument) and data_type.arg_type == 'standard':
            data_type.arg_type = 'str_input'
        if action != 'store':
            data_type = 'bool'
        self.argument = argument
        self.arg_type = arg_type
        self.data_type = data_type
        self.choices = choices
        if self.arg_type != 'standard':
            action = 'store_true'
        self.action = action
        self.description = description
        self.positional = positional
        self.default_value = default_value
        self.size_limit=size_limit
        self.depends_on = depends_on
        self.mutually_exclusive_with = mutually_exclusive_with

        self.truncated_arg = None
        self.full_arg = f"--{self.argument}"

    def verify_standard_value(self, value):
        if self.arg_type == "standard":
            #print(f"ARGUMENT NAME: {self.argument}\nARGUMENT VALUE: {value}\n")
            if value == None and self.default_value:
                value = self.default_value
                return value
            elif not value:
                return value
            min_, max_ = self.size_limit
            try:
                value = self.type_map[self.data_type](value)
            except:
                raise ValueError(f"The argument {self.argument} requires a datatype {self.data_type}")
            if type(value) == int:
                if value >= max_ or value < min_:
                    raise ValueError(f"The argument {self.argument} must be a value in the range {self.size_limit}")
            elif type(value) == str and (len(value) >= max_ or len(value) < min_):
                raise ValueError(f"The argument {self.argument} must be between the sizes {self.size_limit}")
            elif self.choices and value not in self.choices:
                raise ValueError(f"The value for argument {self.argument} must be in the list {self.choices}")
            elif value == None and self.default_value:
                value = self.default_value
        return value

    def json(self):
        json = {
            'name':self.argument,
            'arg_type':self.arg_type,
            'data_type':self.data_type,
            'choices':self.choices,
            'action':self.action,
            'description':self.description,
            'positional':self.positional,
            'default_value':self.default_value,
            'size_limit':self.size_limit,
            'truncated_arg':self.truncated_arg,
            'full_arg':self.full_arg,
            'depends_on':self.depends_on,
            'mutually_exclusive_with':self.mutually_exclusive_with
        }
        if self.data_type in ('string', 'int', 'bool'):
            json['data_type'] = self.data_type
        else:
            json['data_type'] = self.data_type.json() 
        return json
    
    def help_message(self):
        help = {"name":self.argument,
                "description":f"{self.description}"}
        if self.choices and isinstance(self.choices, list):
            help['choices'] = self.choices
        if self.positional:
            help['syntax'] = f"<{self.argument}>"
        elif self.action == 'store':
            help['syntax'] = f"{self.truncated_arg}/{self.full_arg} <{self.argument}>"
        else:
            help['syntax'] = f"{self.truncated_arg}/{self.full_arg}"
            if self.arg_type != 'standard':
                help['syntax'] = help['syntax'] + " (f)"
        return help
    
    def check_for_copy_data(self):
        return {
            'name':self.argument,
            'action':self.action,
        }
    
    def str(self):
        help_str = f"{self.truncated_arg}/{self.full_arg} "
        if self.positional:
            help_str = f"<{self.argument}> "
        elif self.action == 'store':
            help_str += f"<{self.argument}> "
        if self.arg_type != 'standard':
            help_str += ' (f) '
        return help_str


class Form(Argument):
    def __init__(self, form_name, arguments_list, description=None, depends_on=None, flattening_type: typing.Literal['NONE', 'FLATTEN', 'RETRIEVE']='NONE'):
        super().__init__(form_name, arg_type='form', description=description, depends_on=depends_on)
        for argument in arguments_list:
            if argument.arg_type == 'standard':
                argument.arg_type = 'str_input'
        self.arguments_list = {argument.argument:argument for argument in arguments_list}
        self.flattening_type = flattening_type
    
    def flatten_form_data(self, kwargs, target):
        if self.flattening_type == 'FLATTEN':
            form_info = kwargs.pop(target)
            flattened_form_info = {target:True}
            flattened_form_info.update(**{arg_name:arg_value for arg_name, arg_value in form_info.items()})
            return flattened_form_info
        if self.flattening_type == 'RETRIEVE':
            form = kwargs.pop(target)
            exctracted_form_data = {arg_name:arg for arg_name, arg in form.items()}
            return exctracted_form_data
        else:
            return None

    def json(self):
        fields = {argument_name:argument.json() for argument_name, argument in self.arguments_list.items()}
        json = {
            'name':self.argument,
            'arg_type':self.arg_type,
            'data_type':self.data_type,
            'choices':self.choices,
            'action':self.action,
            'description':self.description,
            'positional':self.positional,
            'default_value':self.default_value,
            'size_limit':self.size_limit,
            'truncated_arg':self.truncated_arg,
            'full_arg':self.full_arg,
            'arguments_list':fields
        }
        return json
    

class RequestHandler:
    def handle_requests(self, request):
        pass
    

if __name__ == "__main__":
    pass
    

