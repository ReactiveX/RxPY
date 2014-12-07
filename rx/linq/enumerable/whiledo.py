from rx.internal import Enumerable, Enumerator
from rx.internal import extends

@extends(Enumerable)
class EnumerableWhileDo(object):


    @classmethod
    def while_do(cls, condition, source):
        def next():
            while condition(source):
                yield source

            raise StopIteration()
        return Enumerable(next())

