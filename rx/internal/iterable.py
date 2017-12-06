import itertools

from .basic import identity


class Iterable(object):

    def __init__(self, iterator):
        self._iterator = iterator

    def __iter__(self):
        return self._iterator

    def where(self, predicate):
        return Iterable(value for value in self if predicate(value))

    def select(self, selector=None):
        selector = selector or identity
        return Iterable(selector(value) for value in self)

    def take(self, count):
        def next():
            n = count

            for value in self:
                if n <= 0:
                    raise StopIteration
                n -= 1
                yield value

            raise StopIteration
        return Iterable(next())

    @classmethod
    def range(cls, start, count):
        def next():
            value = start
            n = count
            while n > 0:
                yield value
                value += 1
                n -= 1

            raise StopIteration
        return Iterable(next())

    @classmethod
    def repeat(cls, value, count=None):
        if count is not None:
            return Iterable(value for _ in range(count))
        return Iterable(itertools.repeat(value))

    @classmethod
    def for_each(cls, source, selector=None):
        selector = selector or identity
        return Iterable(selector(value) for value in source)
