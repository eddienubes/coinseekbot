import inspect


def some_method(str: str) -> None:
    print("Hello, world!")

class SomeClass:
    def __init__(self):
        pass

    def some_method(self, str: str) -> None:
        print("Hello, world!")
        
class SomeClass2:
    def __init__(self):
        pass

    def some_method(self, str: str) -> None:
        print("Hello, world!")
        
instance = SomeClass()

print(inspect.signature(some_method).parameters)
