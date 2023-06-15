"""
DECORATORS
These decorators are used in the tapisObjectWrappers.py file to standardize special functions. Allows for increased code reusability
"""
import typing
import time
import abc
import socket
from functools import update_wrapper, partial

try:
    from socketopts import schemas
    from utilities import exceptions, killableThread
except:
    from ..socketopts import schemas
    from ..utilities import exceptions, killableThread


class BaseRequirementDecorator(abc.ABC):
    username: typing.Optional[str] = None
    password: typing.Optional[str] = None

    @abc.abstractmethod
    async def __call__(self, command: typing.Type[object], connection: socket.socket, *args, **kwargs):
        pass


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
                auth_request = schemas.FormRequest(request_content={"password":None},
                                                   message={"message":"Password is required to continue. If you logged in using TACC password login, use that. Otherwise use the session password"})
                requires_username = False
            else:
                auth_request = schemas.FormRequest(request_content={"password":None, "username":None},
                                                   message={"message":"Password is required to continue. If you logged in using TACC password login, use that. Otherwise use the session password\nYour username was returned during initial login"})
            await connection.send(auth_request)
            auth_data = await connection.receive()
            if auth_data.request_content['password'] != self.password and self.password:
                raise ValueError("The provided password does not match the stored password")
            if ((requires_username and auth_data.request_content['password'] != self.password) or (not requires_username and kwargs['username'] != self.username)) and self.username:
                raise ValueError("The provided username does not match the stored username")
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
            confirmation_request = schemas.FormRequest(message={"message":f"YOU REQUESTED TO {command.__class__.__name__.upper()}. THIS MIGHT CAUSE DATA LOSS! Please confirm (y/n)"},
                                                       request_content={"confirmation":None})
            await connection.send(confirmation_request)
            confirmation_reply: schemas.FormResponse = await connection.receive()
            confirmed = confirmation_reply.request_content['confirmation']
            if not confirmed:
                raise exceptions.NoConfirmationError(command)
        return await command.run(**kwargs)


DECORATOR_LIST = [
    NeedsConfirmation,
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