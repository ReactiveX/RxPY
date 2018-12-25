from typing import Callable, Any
from rx.internal import Iterable, AnonymousIterable


def while_do(condition: Callable[[Any], bool], source: Iterable) -> Iterable:
    def _next():
        while condition(source):
            yield source

    return AnonymousIterable(_next())
