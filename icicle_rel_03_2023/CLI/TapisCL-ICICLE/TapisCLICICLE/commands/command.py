from typing import Callable, Optional, Union
from abc import abstractmethod

try:
    from ..utilities.decorators import Auth, NeedsConfirmation, RequiresExpression, RequiresForm, SecureInput
    from ..utilities.decorators import exceptions
except:
    import utilities.decorators as decorators
    import utilities.exceptions as exceptions


class CommandMetaclass(type):
    def __new__(self, cls, name, bases, attrs):
        upper_class = bases[-1]
        object_doc = upper_class.__doc__ 
        if not object_doc or 


class Command:
    def __init__(self, decorator: Union[Auth, NeedsConfirmation, RequiresExpression, RequiresForm, SecureInput]=None):
        self.decorator = decorator

    @abstractmethod
    def run(self):
        pass

    async def __call__(self, **kwargs):
        if self.decorator:
            return await self.decorator(self.run, **kwargs)
        return await self.run(**kwargs)
