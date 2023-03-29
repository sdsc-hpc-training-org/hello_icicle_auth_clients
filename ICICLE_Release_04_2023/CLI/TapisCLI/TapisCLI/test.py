# def metafunction(zeguma):
#     def test(func):
#         def inner(*args, **kwargs):
#             return func()
#         return inner
#     return test


# @metafunction
# def silliness():
#     pass


# print(silliness.__repr__())

# class Silly:
#     def setup(self):
#         print("doing stuff")
#         def __repr__(self):
#             return "awooga"
#         self.__repr__ = __repr__(self)
#     def __str__(self):
#         return "zeugma"


# silly = Silly()
# print(silly)
# silly.setup()
# print(silly)

# import time
# import sys


# animation = ['|','/','-','\\']
# while True:
#     for frame in animation:
#         sys.stdout.write('\rloading ' + frame)
#         sys.stdout.flush()
#         time.sleep(0.1)


# x = {1:0, 3:4}
# if 1 in x and 3 in x:
#     if x[1] and x[3]:
#         print(True)
#     else:
#         print(False)

from helpers import KillableThread
import time
import sys


class Silly:
    def hellothree(self):
        while True:
            print("hello")
            time.sleep(0.5)


silly = Silly()
hellothread = KillableThread(target=silly.hellothree)
hellothread.start()
time.sleep(3)
print("shutting down")
#sys.exit()
hellothread.kill()

