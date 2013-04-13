import itertools

from .basic import identity

class Enumerable(object):
    def __init__(self, iterator):
        self._iterator = iterator
        
    def __iter__(self):
        return  self._iterator.__iter__()

    def where(self, predicate):
        return Enumerable(value for value in self if predicate(value))

    def select(self, selector=None):
        selector = selector or identity
        return Enumerable(selector(value) for value in self)

    def take(self, count):
        def iterator():
            n = count

            for value in self:
                if n <= 0:
                    raise StopIteration
                n -= 1
                yield value
            
            raise StopIteration
        return Enumerable(iterator())   

    @classmethod
    def range(cls, start, count):
        def iterator():
            value = start
            n = count
            while n > 0:
                yield value
                value += 1
                n -= 1

            raise StopIteration
        return cls(iterator())

    @classmethod
    def repeat(cls, value, count=None):
        if not count is None:
            return cls(value for _ in range(count))
        return cls(itertools.repeat(value))

    @classmethod
    def for_each(cls, source, selector=None):
        selector = selector or identity
        return Enumerable(selector(value) for value in source)