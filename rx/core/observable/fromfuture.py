from asyncio.futures import Future

from rx.core import typing
from rx.core import Observable, AnonymousObservable, Disposable


def from_future(future: Future) -> Observable:
    """Converts a Future to an Observable sequence

    Args:
        future -- A Python 3 compatible future.
            https://docs.python.org/3/library/asyncio-task.html#future
            http://www.tornadoweb.org/en/stable/concurrent.html#tornado.concurrent.Future

    Returns:
        An Observable sequence which wraps the existing future success
        and failure.
    """

    def subscribe(observer: typing.Observer, scheduler: typing.Scheduler = None) -> typing.Disposable:
        def done(future):
            try:
                value = future.result()
            except Exception as ex:
                observer.on_error(ex)
            else:
                observer.on_next(value)
                observer.on_completed()

        future.add_done_callback(done)

        def dispose() -> None:
            if future and future.cancel:
                future.cancel()

        return Disposable.create(dispose)

    return AnonymousObservable(subscribe)
