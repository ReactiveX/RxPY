from functools import update_wrapper
from types import FunctionType
from typing import cast, Any, Callable, Iterable, Optional

from rx.core import typing
from rx.disposable import CompositeDisposable


def subscribe(observable: typing.Observable,
              observer: typing.Observer,
              scheduler: Optional[typing.Scheduler] = None
              ) -> typing.Disposable:
    return observable.subscribe(observer.on_next,
                                observer.on_error,
                                observer.on_completed,
                                scheduler=scheduler)


def add_ref(xs, r):
    from rx.core import Observable

    def subscribe_observer(observer: typing.Observer,
                           scheduler: Optional[typing.Scheduler] = None
                           ) -> typing.Disposable:
        return CompositeDisposable(r.disposable,
                                   subscribe(xs, observer, scheduler=scheduler))

    return Observable(subscribe_observer=subscribe_observer)


def is_future(fut: Any) -> bool:
    return callable(getattr(fut, 'add_done_callback', None))


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
    kwargs = {
        'name': name,
        'argdefs': _fun.__defaults__,
        'closure': _fun.__closure__
    }
    alias = FunctionType(*args, **kwargs)  # type: ignore
    alias = cast(FunctionType, update_wrapper(alias, _fun))
    alias.__kwdefaults__ = _fun.__kwdefaults__
    alias.__doc__ = doc
    return alias


class NotSet:
    """Sentinel value."""

    def __eq__(self, other):
        return self is other

    def __repr__(self):
        return 'NotSet'
