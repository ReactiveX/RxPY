from rx.internal import Iterable, AnonymousIterable


def while_do(condition, source):
    def _next():
        while condition(source):
            yield source

        raise StopIteration()
    return AnonymousIterable(_next())
