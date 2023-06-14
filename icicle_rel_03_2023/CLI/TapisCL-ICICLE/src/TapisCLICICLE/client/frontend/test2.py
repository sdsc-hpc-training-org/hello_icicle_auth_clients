import time
from blessed import Terminal
term = Terminal()

class Silly():
    location = (1,2)

start = time.time()
x, y = Silly().location
print(time.time()-start)