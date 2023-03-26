class TimeoutError(Exception):
    """
    Raise exception when timeout time has been exceeded
    """
    def __init__(self):
        super().__init__("Disconnected due to inactivity. Please login again")

    def __str__(self):
        return "Disconnected due to inactivity. Please login again"


class CommandNotFoundError(Exception):
    """
    Raise exception when a command isnt found
    """
    def __init__(self, command):
        self.command = command
        super().__init__(f"Command {command} was not found in the command list. See help")
    
    def __str__(self):
        return f"Command {self.command} was not found in the command list. See help"

class Shutdown(Exception):
    """
    raise error when a shutdown is initiated
    """
    def __init__(self):
        super().__init__(f"shutdown initiated")

    def __str__(self):
        return "shutdown initiated"


class Exit(Exception):
    """
    raise error when an exit is initiated
    """
    def __init__(self):
        super().__init__(f"exit initiated")

    def __str__(self):
        return "exit initiated"