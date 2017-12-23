import itertools
from collections import abc

from .basic import identity


class Iterable(abc.Iterable):

    def filter(self, predicate):
        from .anonymousiterable import AnonymousIterable
        return AnonymousIterable(value for value in self if predicate(value))

    def map(self, selector=None):
        selector = selector or identity

        return Iterable(selector(value) for value in self)

    def take(self, count):
        def _next():
            n = count

            for value in self:
                if n <= 0:
                    raise StopIteration
                n -= 1
                yield value

            raise StopIteration

        from .anonymousiterable import AnonymousIterable
        return AnonymousIterable(_next())

    @staticmethod
    def range(start, count):
        def _next():
            value = start
            n = count
            while n > 0:
                yield value
                value += 1
                n -= 1

            raise StopIteration

        from .anonymousiterable import AnonymousIterable
        return AnonymousIterable(_next())

    @staticmethod
    def repeat(value, count=None):
        from .anonymousiterable import AnonymousIterable
        if count is not None:
            return AnonymousIterable(value for _ in range(count))

        return AnonymousIterable(itertools.repeat(value))

    @staticmethod
    def for_each(source, selector=None):
        selector = selector or identity

        from .anonymousiterable import AnonymousIterable
        return AnonymousIterable(selector(value) for value in source)

    @staticmethod
    def while_do(condition, source):
        from ..operators.enumerable.whiledo import while_do
        return while_do(condition, source)
