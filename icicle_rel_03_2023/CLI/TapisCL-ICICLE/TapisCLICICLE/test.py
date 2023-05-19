x = {'y':2, 'z': 1, 'v':2}
import inspect
async def silly(y, z, **kwargs):
    print(y)

print(inspect.iscoroutinefunction(silly))
