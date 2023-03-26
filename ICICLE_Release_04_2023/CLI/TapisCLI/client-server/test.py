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

class Silly:
    def setup(self):
        print("doing stuff")
        def __repr__(self):
            return "awooga"
        self.__repr__ = __repr__(self)
    def __str__(self):
        return "zeugma"


silly = Silly()
print(silly)
silly.setup()
print(silly)