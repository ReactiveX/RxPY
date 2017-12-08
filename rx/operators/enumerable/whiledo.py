from rx.internal import Iterable, AnonymousIterable
from rx.internal import extensionclassmethod

@extensionclassmethod(Iterable)
def while_do(cls, condition, source):
    def _next():
        while condition(source):
            yield source

        raise StopIteration()
    return AnonymousIterable(_next())
