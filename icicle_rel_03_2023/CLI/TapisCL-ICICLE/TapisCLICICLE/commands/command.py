from typing import Callable, Optional, Union
try:
    from ..utilities.decorators import Auth, NeedsConfirmation, RequiresExpression, RequiresForm, SecureInput
except:
    import utilities.decorators as decorators


class Command:
    def __init__(self, decorator: Union[Auth, NeedsConfirmation, RequiresExpression, RequiresForm, SecureInput]=None):
        self.decorator = decorator

    async def __call__(self, **kwargs):
        if self.decorator:
            return await self.decorator(self.method, **kwargs)
        return await self.method(**kwargs)
