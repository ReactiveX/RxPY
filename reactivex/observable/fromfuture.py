import asyncio
from asyncio import Future
from typing import Any, Optional, TypeVar, cast

from reactivex import Observable, abc
from reactivex.disposable import Disposable

_T = TypeVar("_T")


def from_future_(future: "Future[_T]") -> Observable[_T]:
    """Converts a Future to an Observable sequence

    Args:
        future -- A Python 3 compatible future.
            https://docs.python.org/3/library/asyncio-task.html#future

    Returns:
        An Observable sequence which wraps the existing future success
        and failure.
    """

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        def done(future: "Future[_T]") -> None:
            try:
                value: Any = future.result()
            except Exception as ex:
                observer.on_error(ex)
            except asyncio.CancelledError as ex:  # pylint: disable=broad-except
                # asyncio.CancelledError is a BaseException, so need to cast
                observer.on_error(cast(Exception, ex))
            else:
                observer.on_next(value)
                observer.on_completed()

        future.add_done_callback(done)

        def dispose() -> None:
            if future:
                future.cancel()

        return Disposable(dispose)

    return Observable(subscribe)


__all__ = ["from_future_"]
