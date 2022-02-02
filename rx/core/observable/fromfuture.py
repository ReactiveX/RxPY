import asyncio
from typing import Any, Optional

from rx.core import Observable, abc, typing
from rx.disposable import Disposable


def _from_future(future: typing.Future) -> Observable[Any]:
    """Converts a Future to an Observable sequence

    Args:
        future -- A Python 3 compatible future.
            https://docs.python.org/3/library/asyncio-task.html#future
            http://www.tornadoweb.org/en/stable/concurrent.html#tornado.concurrent.Future

    Returns:
        An Observable sequence which wraps the existing future success
        and failure.
    """

    def subscribe(observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None) -> abc.DisposableBase:
        def done(future: typing.Future):
            try:
                value: Any = future.result()
            except (Exception, asyncio.CancelledError) as ex:  # pylint: disable=broad-except
                observer.on_error(ex)
            else:
                observer.on_next(value)
                observer.on_completed()

        future.add_done_callback(done)

        def dispose() -> None:
            if future and future.cancel:
                future.cancel()

        return Disposable(dispose)

    return Observable(subscribe)


__all__ = ["_from_future"]
