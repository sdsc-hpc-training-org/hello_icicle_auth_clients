"""
DECORATORS
These decorators are used in the tapisObjectWrappers.py file to standardize special functions. Allows for increased code reusability
"""
import typing
import enum
import sys
import time
from functools import update_wrapper, partial
try:
    from . import helpers
    from . import schemas
    from . import socketOpts
    from . import exceptions
except:
    import utilities.helpers as helpers
    import utilities.schemas as schemas
    import utilities.socketOpts as socketOpts
    import utilities.exceptions as exceptions


class BaseRequirementDecorator(helpers.OperationsHelper):
    username: typing.Optional[str] = None
    password: typing.Optional[str] = None
    def __init__(self, func: typing.Callable):
        update_wrapper(self, func)
        self.function = func
        self.__code__ = func.__code__
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__
    
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
    """
    This is for when you want to request separate input for specific command parameters instead of taking directly from the original command input (kwargs)
    Takes the parameters list of the function in question, filters out the ones that were not received from the original request message, sends another message 
    to request the unreceived parameters, and receives a message in response from the client to execute the function
    """
    async def __call__(self, obj, *args, **kwargs):
        if kwargs['connection']:
            connection = kwargs['connection']
            fields = list(helpers.get_parameters(self.function))
            for key, value in kwargs.items():
                if value or value == False:
                    fields.remove(key)
            if not fields:
                raise AttributeError(f"The decorated function {self.function} has no parameters.")
            form_request = schemas.FormRequest(arguments_list=fields)
            await connection.send(form_request)
            filled_form: schemas.FormResponse = await connection.receive().arguments_list
            for key, value in filled_form.items():
                kwargs[key] = value

        return await self.function(obj, **kwargs)


class RequiresExpression(BaseRequirementDecorator):
    """
    This is for when you have something like a Neo4j or postgres interface to add to the tapisObjectWrappers file. Writing a Neo4j query directly in a command is cumbersome, its much
    easier to do if you have a blank, multiline environment to write. This will send a request for an expression, if an expression parameter exists in the decorated function.
    The client will open a new interface to type the expression. This is then sent back and fed to the function
    """
    async def __call__(self, obj, *args, **kwargs):
        if kwargs['connection']:
            connection = kwargs['connection']
            fields = list(helpers.get_parameters(self.function))
            if 'expression' not in fields:
                raise AttributeError(f"The function {self.function} does not contain an 'expression' parameter")
            form_request = schemas.FormRequest(arguments_list=[])
            await connection.send(form_request)
            filled_form: schemas.FormResponse = await connection.receive()
            kwargs['expression'] = filled_form.arguments_list

        return await self.function(obj, **kwargs)
    

class SecureInput(BaseRequirementDecorator):
    """
    Use this for functions where you need to hide input while typing into the cli. For instance, if you want to add a password to a service, as a user, but you dont actually
    want to authenticate. Checks if the decorated function has a password parameter, then requests secure input of a new password from the client
    """
    async def __call__(self, obj, *args, **kwargs):
        if kwargs['connection']:
            connection = kwargs['connection']
            fields = list(helpers.get_parameters(self.function))
            if 'password' in fields:
                secure_input_request = schemas.AuthRequest(secure_input=True)
                await connection.send(secure_input_request)
                secure_input_data: schemas.AuthData = await connection.receive()
                kwargs['password'] = secure_input_data.password
                return await self.function(obj, **kwargs)
            raise AttributeError(f"The function {self.function} does not contain a 'password' parameter to securely input")
        return await self.function(obj, **kwargs)


class Auth(BaseRequirementDecorator):
    """
    used for secure authentication from the client. Requires that the function has a username and password parameter for credentials. sends request for credentials from 
    the client, and checks those credentials against the stored credentials in the server.
    """
    async def __call__(self, obj, *args, **kwargs):
        no_username = False
        if kwargs['connection']:
            connection = kwargs['connection']
            if self.function.__name__ == 'tapis_init' and kwargs['username'] and kwargs['password']:
                return await self.function(obj, **kwargs)
            fields = list(helpers.get_parameters(self.function))
            if kwargs['username']:
                no_username = True
                auth_request = schemas.AuthRequest(requires_username=False)
            else:
                auth_request = schemas.AuthRequest()
            await connection.send(auth_request)
            auth_data: schemas.AuthData = await connection.receive()
            if 'username' in fields and 'password' in fields and not no_username:
                kwargs['username'], kwargs['password'] = auth_data.username, auth_data.password
                return await self.function(obj, **kwargs)
            elif 'password' in fields and no_username:
                kwargs['password'] = auth_data.password
            username, password = auth_data.username, auth_data.password
            if username != BaseRequirementDecorator.username:
                raise exceptions.InvalidCredentialsReceived(self.function, 'username')
            elif password != BaseRequirementDecorator.password:    
                raise exceptions.InvalidCredentialsReceived(self.function, 'password')

        return await self.function(obj, **kwargs)


class NeedsConfirmation(BaseRequirementDecorator):
    """
    add to functions that you want user confirmation to exit. If you accidentally enter a command to delete a pod, this will not let you until you confirm
    """
    async def __call__(self, obj, *args, **kwargs):
        if kwargs['connection']:
            connection = kwargs['connection']
            confirmation_request = schemas.ConfirmationRequest(message=f"YOU REQUESTED TO {self.function.__name__}. THIS MIGHT CAUSE DATA LOSS! Please confirm (y/n)")
            await connection.send(confirmation_request)
            confirmation_reply: schemas.ResponseData = await connection.receive()
            confirmed = confirmation_reply.response_message
            if not confirmed:
                raise exceptions.NoConfirmationError(self.function)
        return await self.function(obj, **kwargs)

    
class DecoratorSetup:
    """
    for instantiation of the tapis wrappers, and the server, to set up decorators with user credentials and the socket connection. If you want to use the decorators in your class
    YOU WILL NEED TO USE THIS!
    """
    def configure_decorators(self, username, password):
        BaseRequirementDecorator.username = username
        BaseRequirementDecorator.password = password


class DecoratorUtility:

    def __init__(self, decorator_type: int):
        

class AnimatedLoading:
    """
    Add this if you want to print a loading animation while a function is executing
    """
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
        if not BaseRequirementDecorator.username:
            animation_thread = helpers.KillableThread(target=self.animation)
            animation_thread.start()
            result = self.function(obj, *args, **kwargs)
            sys.stdout.flush()
            animation_thread.kill()
            sys.stdout.flush()
        else:
            result = self.function(obj, *args, **kwargs)
        return result