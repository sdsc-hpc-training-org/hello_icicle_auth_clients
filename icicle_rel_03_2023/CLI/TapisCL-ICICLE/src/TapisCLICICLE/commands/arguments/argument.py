import typing
import abc


ALLOWED_ARG_TYPES = typing.Literal['secure', 'expression', 'input_list', 'input_dict', 'form', 'str_input', 'confirmation']
ALLOWED_DATA_TYPES = typing.Literal['string', 'int']
ALLOWED_ACTIONS = typing.Literal['store', 'store_true', 'store_false']


class DynamicChoiceList(abc.ABC):
    @abc.abstractmethod
    def __call__(self, tapis_instance):
        pass


class AbstractArgument(abc.ABC):
    @abc.abstractmethod
    def json(self):
        pass


class Argument(AbstractArgument):
    def __init__(self, argument: str,
                 data_type: ALLOWED_DATA_TYPES | typing.Type[AbstractArgument] = 'string',
                 arg_type: ALLOWED_ARG_TYPES | typing.Literal['standard']='standard',
                 choices: list | typing.Type[DynamicChoiceList] | None=None, 
                 action: typing.Literal['store', 'store_true', 'store_false']="store", 
                 description: str="",
                 positional: bool=False,
                 default_value=None,
                 size_limit: tuple=(0,4096)):
        if arg_type not in typing.get_args(ALLOWED_ARG_TYPES) and arg_type != 'standard':
            raise ValueError(f"The arg type parameter in the argument {self.__class__.__name__} must be in the list {ALLOWED_ARG_TYPES}. Got arg type {arg_type}")
        if data_type not in typing.get_args(ALLOWED_DATA_TYPES) and not issubclass(data_type.__class__, AbstractArgument):
            raise ValueError(f"The data type argument provided to the argument {self.__class__.__name__} must be in the list {ALLOWED_DATA_TYPES}, or must be a subclass of AbstractArgument")
        if action not in typing.get_args(ALLOWED_ACTIONS):
            raise ValueError(f"Action {action} not in the list {ALLOWED_ACTIONS}, in argument {self.__class__.__name__}")
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

        self.truncated_arg = None
        self.full_arg = None

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
            'full_arg':self.full_arg
        }
        if self.data_type in ('string', 'int'):
            json['data_type'] = self.data_type
        else:
            json['data_type'] = self.data_type.json()
        return json


class Form(Argument):
    def __init__(self, form_name, arguments_list):
        super().__init__(form_name, arg_type='form')
        for argument in arguments_list:
            if argument.arg_type == 'standard':
                argument.arg_type = 'str_input'
        self.arguments_list = {argument.argument:argument for argument in arguments_list}

    def json(self):
        return {argument_name:argument.json() for argument_name, argument in self.arguments_list.items()}
    

class RequestHandler:
    def handle_requests(self, request):
        pass
    

if __name__ == "__main__":
    pass
    

