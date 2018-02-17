from typing import Iterable

from rx.core import ObservableBase, AnonymousObservable
from rx.concurrency import current_thread_scheduler
from rx.disposables import CompositeDisposable, AnonymousDisposable


def from_iterable(iterable: Iterable) -> ObservableBase:
    """Converts an iterable to an observable sequence.

    1 - res = rx.Observable.from_iterable([1,2,3])

    Keyword arguments:
    iterable - An python iterable

    Returns the observable sequence whose elements are pulled from the
    given iterable sequence.
    """

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or current_thread_scheduler
        iterator = iter(iterable)
        disposed = False

        def action(scheduler, state=None):
            nonlocal disposed

            try:
                while not disposed:
                    value = next(iterator)
                    observer.on_next(value)
            except StopIteration:
                observer.on_completed()
            except Exception as error:  # pylint: disable=W0703
                observer.on_error(error)

        def dispose():
            nonlocal disposed
            disposed = True

        disposable = AnonymousDisposable(dispose)
        return CompositeDisposable(scheduler.schedule(action), disposable)
    return AnonymousObservable(subscribe)
