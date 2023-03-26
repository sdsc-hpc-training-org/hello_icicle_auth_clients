import typing
from TypeEnforcement.type_enforcer import TypeEnforcer


def get_parameters(func):
    return func.__code__.co_varnames[:func.__code__.co_argcount]

class OperationsHelper:
    def filter_kwargs(self, func: typing.Callable, kwargs: dict) -> dict:
        filtered = dict()
        variables = list(get_parameters(func))
        variables.remove('self')
        for arg in variables:
            print(arg)
            print(kwargs[arg])
            filtered.update({arg:kwargs[arg]})
        return filtered


if __name__ == "__main__":
    class Silly:
        def z(self, y=True, x=False):
            return None
    x = OperationsHelper()
    v=Silly()
    x.filter_kwargs(v.z, {'y':False, 'x':"True", 'z':"hi"})
    