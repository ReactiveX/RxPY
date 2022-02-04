from asyncio import Future
from functools import update_wrapper
from types import FunctionType
from typing import Any, Callable, Iterable, Optional, cast

from rx.core import abc
from rx.disposable import CompositeDisposable


def add_ref(xs: abc.ObservableBase[Any], r):
    from rx.core import Observable

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ):
        return CompositeDisposable(r.disposable, xs.subscribe(observer))

    return Observable(subscribe)


def is_future(fut: Any) -> bool:
    return isinstance(fut, Future)


def infinite() -> Iterable[int]:
    n = 0
    while True:
        yield n
        n += 1


def alias(name: str, doc: str, fun: Callable[..., Any]) -> Callable[..., Any]:
    # Adapted from https://stackoverflow.com/questions/13503079/how-to-create-a-copy-of-a-python-function#
    # See also help(type(lambda: 0))
    _fun = cast(FunctionType, fun)
    args = (_fun.__code__, _fun.__globals__)
    kwargs = {"name": name, "argdefs": _fun.__defaults__, "closure": _fun.__closure__}
    alias = FunctionType(*args, **kwargs)  # type: ignore
    alias = update_wrapper(alias, _fun)
    alias.__kwdefaults__ = _fun.__kwdefaults__
    alias.__doc__ = doc
    return alias


class NotSet:
    """Sentinel value."""

    def __eq__(self, other: Any):
        return self is other

    def __repr__(self):
        return "NotSet"
