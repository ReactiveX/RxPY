from rx.internal import Iterable
from rx.internal import extensionclassmethod

@extensionclassmethod(Iterable)
def while_do(cls, condition, source):
    def next():
        while condition(source):
            yield source

        raise StopIteration()
    return Iterable(next())

