from functools import update_wrapper
from types import FunctionType
from typing import Any, Callable, Iterable

from rx.disposable import CompositeDisposable


def add_ref(xs, r):
    from rx.core import Observable

    def subscribe(observer, scheduler=None):
        return CompositeDisposable(r.disposable, xs.subscribe(observer))

    return Observable(subscribe)


def is_future(fut: Any) -> bool:
    return callable(getattr(fut, "add_done_callback", None))


def infinite() -> Iterable[int]:
    n = 0
    while True:
        yield n
        n += 1


def alias(name: str, doc: str, fun: Callable[..., Any]) -> Callable[..., Any]:
    # Adapted from https://stackoverflow.com/questions/13503079/how-to-create-a-copy-of-a-python-function#
    # See also help(type(lambda: 0))
    alias = FunctionType(fun.__code__, fun.__globals__,
                         name=name, argdefs=fun.__defaults__,
                         closure=fun.__closure__)
    alias = update_wrapper(alias, fun)
    alias.__kwdefaults__ = fun.__kwdefaults__
    alias.__doc__ = doc
    return alias


class NotSet:
    """Sentinel value."""

    def __eq__(self, other):
        return self is other

    def __repr__(self):
        return 'NotSet'
