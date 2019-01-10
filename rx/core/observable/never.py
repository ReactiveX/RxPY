from rx.core import typing
from rx.core import Observable, AnonymousObservable, Disposable


def _never() -> Observable:
    """Returns a non-terminating observable sequence, which can be used
    to denote an infinite duration (e.g. when using reactive joins).

    Returns:
        An observable sequence whose observers will never get called.
    """

    def subscribe(_: typing.Observer, __: typing.Scheduler = None) -> typing.Disposable:
        return Disposable.empty()

    return AnonymousObservable(subscribe)
