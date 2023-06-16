import typing


class TimeoutError(Exception):
    """
    Raise exception when timeout time has been exceeded
    """
    def __init__(self):
        super().__init__("Disconnected due to inactivity. Please login again")


class CommandNotFoundError(Exception):
    """
    Raise exception when a command isnt found
    """
    def __init__(self, command: str):
        self.command = command
        super().__init__(f"Command {command} was not found in the command list. See help")
    

class Shutdown(Exception):
    """
    raise error when a shutdown is initiated
    """
    def __init__(self):
        super().__init__(f"shutdown initiated")


class Exit(Exception):
    """
    raise error when an exit is initiated
    """
    def __init__(self):
        super().__init__(f"exit initiated")
    

class NoConfirmationError(Exception):
    """
    raise error when no confirmation is given for a function that needs confirmation to continue
    """
    def __init__(self, function: typing.Callable):
        super().__init__(f"Confirmation was not given to the function {function.__class__.__name__}")


class InvalidCredentialsReceived(Exception):
    """
    raise error when the provided credentials fail
    """
    def __init__(self, *args):
        super().__init__(*args)


class HelpDoesNotExist(AttributeError):
    """
    raise error when the program tries to extract help information from a method, but help is not found
    """
    def __init__(self, command_name):
        super().__init__(f"The command {command_name} has no help menu.\nMust include a docstring with @help: <help information>")


class UnauthorizedAccessError(Exception):
    """
    raise error when an unauthorized IP tries to connect to the server
    """
    def __init__(self, ip):
        super().__init__(f"DANGER! UNAUTHORIZED IP {ip} TRIED TO CONNECT TO THE SERVER. SOMEONE IS TRYING TO PIGGYBACK ON THE TAPIS APPLICATION, AND ATTEMPTING TO STEAL YOUR DATA.")


class ClientSideError(ConnectionError):
    """
    raise error when problem is on client side
    """
    def __init__(self, error_message):
        super().__init__(f"CLIENT SIDE ERROR: {error_message}")


class NoTenantClient(AttributeError):
    """
    raise error when no client for tenant for auth
    """
    def __init__(self, tenant):
        super().__init__(f"No client found for the tenant {tenant}")