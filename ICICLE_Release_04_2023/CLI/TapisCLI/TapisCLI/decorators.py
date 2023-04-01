import typing
import socket
import sys
import time
import functools
from functools import update_wrapper, partial
try:
    from . import helpers
    from . import schemas
    from . import SocketOpts
    from . import exceptions
except:
    import helpers
    import schemas
    import SocketOpts
    import exceptions


class BaseRequirementDecorator(SocketOpts.SocketOpts, helpers.OperationsHelper):
    connection: typing.Optional[socket.socket] = None
    username: typing.Optional[str] = None
    password: typing.Optional[str] = None
    def __init__(self, func: typing.Callable):
        update_wrapper(self, func)
        self.function = func
        self.__code__ = func.__code__
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__
        self.connection = BaseRequirementDecorator.connection
        self.username = BaseRequirementDecorator.username
        self.password = BaseRequirementDecorator.password
    
    def __get__(self, obj, objtype): 
        """Support instance methods."""
        part = partial(self.__call__, obj)
        part.__code__ = self.__code__
        part.__doc__ = self.__doc__
        part.__name__ = self.__name__
        return part
    
    def __repr__(self):
        return str(self.function)
    
    def __str__(self):
        return str(self.function)


class RequiresForm(BaseRequirementDecorator):
    def __call__(self, obj, *args, **kwargs):
        fields = list(helpers.get_parameters(self.function))
        if not fields:
            raise AttributeError(f"The decorated function {self.function} has no parameters.")
        form_request = schemas.FormRequest(arguments_list=fields)
        self.json_send(form_request.dict())
        filled_form: schemas.FormResponse = self.schema_unpack().arguments_list

        return self.function(obj, **filled_form)


class RequiresExpression(BaseRequirementDecorator):
    def __call__(self, obj, *args, **kwargs):
        fields = list(helpers.get_parameters(self.function))
        if 'expression' not in fields:
            raise AttributeError(f"The function {self.function} does not contain an 'expression' parameter")
        form_request = schemas.FormRequest(arguments_list=[])
        self.json_send(form_request.dict())
        filled_form: schemas.FormResponse = self.schema_unpack()
        kwargs['expression'] = filled_form.arguments_list

        return self.function(obj, **kwargs)
    

class SecureInput(BaseRequirementDecorator):
    def __call__(self, obj, *args, **kwargs):
        fields = list(helpers.get_parameters(self.function))
        if 'password' in fields:
            secure_input_request = schemas.AuthRequest(secure_input=True)
            self.json_send(secure_input_request.dict())
            secure_input_data: schemas.AuthData = self.schema_unpack()
            kwargs['password'] = secure_input_data.password
            return self.function(**kwargs)
        raise AttributeError(f"The function {self.function} does not contain a 'password' parameter")


class Auth(BaseRequirementDecorator):
    def __call__(self, obj, *args, **kwargs):
        if self.function.__name__ == 'tapis_init' and kwargs['username'] and kwargs['password']:
            return self.function(obj, **kwargs)
        fields = list(helpers.get_parameters(self.function))
        auth_request = schemas.AuthRequest()
        self.json_send(auth_request.dict())
        auth_data: schemas.AuthData = self.schema_unpack()
        if 'username' in fields and 'password' in fields:
            kwargs['username'], kwargs['password'] = auth_data.username, auth_data.password
            return self.function(**kwargs)
        username, password = auth_data.username, auth_data.password
        if username != self.username:
            raise exceptions.InvalidCredentialsReceived(self.function, 'username')
        elif password != self.password:    
            raise exceptions.InvalidCredentialsReceived(self.function, 'password')

        return self.function(obj, **kwargs)


class NeedsConfirmation(BaseRequirementDecorator):
    def __call__(self, obj, *args, **kwargs):
        confirmation_request = schemas.ConfirmationRequest(message=f"You requested to {self.function.__name__}. Please confirm (y/n)")
        self.json_send(confirmation_request.dict())
        confirmation_reply: schemas.ResponseData = self.schema_unpack()
        confirmed = confirmation_reply.response_message
        if not confirmed:
            raise exceptions.NoConfirmationError(self.function)
        return self.function(obj, **kwargs)
    

class DecoratorSetup:
    decorators_list = [RequiresForm, Auth, NeedsConfirmation, RequiresExpression]
    def configure_decorators(self):
        for decorator in DecoratorSetup.decorators_list:
            decorator.connection = self.connection
            decorator.username = self.username
            decorator.password = self.password
    

class AnimatedLoading:
    def __init__(self, func: typing.Callable):
        update_wrapper(self, func)
        self.function = func
        self.__code__ = func.__code__
        self.animation_frames = ['|','/','-','\\']

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return partial(self.__call__, obj)

    def __repr__(self):
        return self.function
    
    def __str__(self):
        return str(self.function)
    
    def animation(self):
        while True:
            for frame in self.animation_frames:
                sys.stdout.write(f'\rloading ' + frame)
                sys.stdout.flush()
                time.sleep(0.5)
    
    def __call__(self, obj, *args, **kwargs):
        animation_thread = helpers.KillableThread(target=self.animation)
        animation_thread.start()
        result = self.function(obj, *args, **kwargs)
        animation_thread.kill()
        return result


