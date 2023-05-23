"""
DECORATORS
These decorators are used in the tapisObjectWrappers.py file to standardize special functions. Allows for increased code reusability
"""
import typing
import enum
import sys
import time
import abc
import socket
from functools import update_wrapper, partial
try:
    from ..utilities import killableThread
    from ..utilities import schemas
    from ..utilities import socketOpts
    from ..utilities import exceptions
except:
    import killableThread
    import schemas
    import socketOpts
    import exceptions
    

class BaseRequirementDecorator(abc.ABC):
    username: typing.Optional[str] = None
    password: typing.Optional[str] = None

    @abc.abstractmethod
    async def __call__(self, command: typing.Type[object], connection: socket.socket, *args, **kwargs):
        pass


class RequiresForm(BaseRequirementDecorator):
    """
    This is for when you want to request separate input for specific command parameters instead of taking directly from the original command input (kwargs)
    Takes the parameters list of the function in question, filters out the ones that were not received from the original request message, sends another message 
    to request the unreceived parameters, and receives a message in response from the client to execute the function
    """
    async def __call__(self, command, *args, **kwargs):
        connection = kwargs['connection']
        if connection and not kwargs['file']:
            connection = connection
            fields = command.keyword_arguments
            if not fields:
                raise AttributeError(f"The decorated function {command} has no keyword parameters.")
            form_request = schemas.FormRequest(arguments_list=fields)
            await connection.send(form_request)
            filled_form: schemas.FormResponse = await connection.receive()
            for key, value in filled_form.arguments_list.items():
                kwargs[key] = value

        return await command.run(**kwargs)


class RequiresExpression(BaseRequirementDecorator):
    """
    This is for when you have something like a Neo4j or postgres interface to add to the tapisObjectWrappers file. Writing a Neo4j query directly in a command is cumbersome, its much
    easier to do if you have a blank, multiline environment to write. This will send a request for an expression, if an expression parameter exists in the decorated function.
    The client will open a new interface to type the expression. This is then sent back and fed to the function
    """
    async def __call__(self, command, *args, **kwargs):
        connection = kwargs['connection']
        if connection:
            connection = connection
            if 'expression' not in command.keyword_arguments:
                raise AttributeError(f"The function {command} does not contain an 'expression' keyword parameter")
            form_request = schemas.FormRequest(arguments_list=[])
            await connection.send(form_request)
            filled_form: schemas.FormResponse = await connection.receive()
            kwargs['expression'] = filled_form.arguments_list

        return await command.run(**kwargs)
    

class SecureInput(BaseRequirementDecorator):
    """
    Use this for functions where you need to hide input while typing into the cli. For instance, if you want to add a password to a service, as a user, but you dont actually
    want to authenticate. Checks if the decorated function has a password parameter, then requests secure input of a new password from the client
    """
    async def __call__(self, command, *args, **kwargs):
        connection = kwargs['connection']
        if connection:
            connection = connection
            if 'password' in command.keyword_arguments:
                secure_input_request = schemas.AuthRequest(secure_input=True)
                await connection.send(secure_input_request)
                secure_input_data: schemas.AuthData = await connection.receive()
                kwargs['password'] = secure_input_data.password
                return await command.run(**kwargs)
            raise AttributeError(f"The function {command} does not contain a 'password' parameter to securely input")
        return await command.run(**kwargs)


class Auth(BaseRequirementDecorator):
    """
    used for secure authentication from the client. Requires that the function has a username and password parameter for credentials. sends request for credentials from 
    the client, and checks those credentials against the stored credentials in the server.
    """
    async def __call__(self, command, *args, **kwargs):
        connection = kwargs['connection']
        requires_username = True
        if connection:
            if 'password' not in command.keyword_arguments:
                raise AttributeError(f"The command {command.__class__.__name__} does not have a 'password' keyword argument")
            if 'username' not in command.keyword_arguments:
                auth_request = schemas.AuthRequest(requires_username=False)
                requires_username = False
            else:
                auth_request = schemas.AuthRequest()
            await connection.send(auth_request)
            auth_data = await connection.receive()
            if auth_data.password != self.password and self.password:
                raise ValueError("The provided password does not match the stored password")
            if ((requires_username and auth_data.username != self.password) or (not requires_username and kwargs['username'] != self.username)) and self.username:
                raise ValueError("The provided username does not match the stored username")
            print(kwargs)
            kwargs['username'], kwargs['password'] = auth_data.username, auth_data.password
            return await command.run(**kwargs)
        return await command.run(**kwargs)


class NeedsConfirmation(BaseRequirementDecorator):
    """
    add to functions that you want user confirmation to exit. If you accidentally enter a command to delete a pod, this will not let you until you confirm
    """
    async def __call__(self, command, *args, **kwargs):
        connection = kwargs['connection']
        if connection:
            connection = connection
            confirmation_request = schemas.ConfirmationRequest(message=f"YOU REQUESTED TO {command.__class__.__name__}. THIS MIGHT CAUSE DATA LOSS! Please confirm (y/n)")
            await connection.send(confirmation_request)
            confirmation_reply: schemas.ResponseData = await connection.receive()
            confirmed = confirmation_reply.response_message
            if not confirmed:
                raise exceptions.NoConfirmationError(command)
        return await command.run(**kwargs)


DECORATOR_LIST = [
    NeedsConfirmation,
    RequiresForm,
    RequiresExpression,
    SecureInput,
    Auth
]
    
class DecoratorSetup:
    """
    for instantiation of the tapis wrappers, and the server, to set up decorators with user credentials and the socket connection. If you want to use the decorators in your class
    YOU WILL NEED TO USE THIS!
    """
    def configure_decorators(self, username, password):
        self.username = username
        self.password = password


class AnimatedLoading:
    """
    Add this if you want to print a loading animation while a function is executing
    """
    def __init__(self, func: typing.Callable):
        update_wrapper(self, func)
        self.func = func
        self.__code__ = func.__code__
        self.animation_frames = ['|','/','-','\\']

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return partial(self.__call__, obj)

    def __repr__(self):
        return self.func
    
    def __str__(self):
        return str(self.func)
    
    def animation(self):
        while True:
            for frame in self.animation_frames:
                print(f"loading {frame}", end='', flush=True)
                time.sleep(0.5)
    
    def __call__(self, obj, *args, **kwargs):
        animation_thread = killableThread.KillableThread(target=self.animation)
        animation_thread.start()
        result = self.func(obj, *args, **kwargs)
        animation_thread.kill()
        print("", end='', flush=True)
        return result
    

if __name__ == "__main__":
    print(issubclass(RequiresExpression, BaseRequirementDecorator))