from typing import Iterable, Any

from rx.core import Observable, AnonymousObservable, typing
from rx.concurrency import current_thread_scheduler
from rx.disposable import CompositeDisposable, AnonymousDisposable


def from_iterable(iterable: Iterable, scheduler: typing.Scheduler = None) -> Observable:
    """Converts an iterable to an observable sequence.

    Example:
        >>> from_iterable([1,2,3])

    Args:
        iterable: A Python iterable
        scheduler: An optional scheduler to schedule the values on.

    Returns:
        The observable sequence whose elements are pulled from the
        given iterable sequence.
    """

    def subscribe(observer: typing.Observer, scheduler_: typing.Scheduler = None) -> typing.Disposable:
        _scheduler = scheduler or scheduler_ or current_thread_scheduler
        iterator = iter(iterable)
        disposed = False

        def action(_: typing.Scheduler, __: Any = None) -> None:
            nonlocal disposed

            try:
                while not disposed:
                    value = next(iterator)
                    observer.on_next(value)
            except StopIteration:
                observer.on_completed()
            except Exception as error:  # pylint: disable=broad-except
                observer.on_error(error)

        def dispose() -> None:
            nonlocal disposed
            disposed = True

        disp = AnonymousDisposable(dispose)
        return CompositeDisposable(_scheduler.schedule(action), disp)
    return AnonymousObservable(subscribe)
