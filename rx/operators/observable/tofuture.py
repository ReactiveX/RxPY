from typing import Callable
from asyncio import Future

from rx.core import ObservableBase


def to_future(source: ObservableBase, future_ctor: Callable[[], Future] = None) -> Future:
    """Converts an existing observable sequence to a Future.

    Example:
    future = rx.Observable.return_value(42).to_future(trollius.Future);

    With config:
    rx.config["Future"] = trollius.Future
    future = rx.Observable.return_value(42).to_future()

    future_ctor -- {Functi[Optional] The constructor of the future.
        If not provided, it looks for it in rx.config.Future.

    Returns a future with the last value from the observable sequence.
    """

    future_ctor = future_ctor or Future
    future = future_ctor()

    value = [None]
    has_value = [False]

    def on_next(v):
        value[0] = v
        has_value[0] = True

    def on_error(err):
        future.set_exception(err)

    def on_completed():
        if has_value[0]:
            future.set_result(value[0])

    source.subscribe_(on_next, on_error, on_completed)

    # No cancellation can be done
    return future

