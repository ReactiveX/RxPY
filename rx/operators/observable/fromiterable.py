from typing import Iterable

from rx import config
from rx.core import Observable, AnonymousObservable
from rx.concurrency import current_thread_scheduler
from rx.disposables import MultipleAssignmentDisposable


def from_iterable(iterable: Iterable, delay: int = None) -> Observable:
    """Converts an array to an observable sequence, using an optional
    scheduler to enumerate the array.

    1 - res = rx.Observable.from_iterable([1,2,3])

    Keyword arguments:
    iterable - An python iterable

    Returns the observable sequence whose elements are pulled from the
        given enumerable sequence.
    """
    lock = config["concurrency"].RLock()

    delay = delay or 0

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or current_thread_scheduler
        print(scheduler)

        mad = MultipleAssignmentDisposable()
        iterator = iter(iterable)

        def action(scheduler, state=None):
            nonlocal observer, mad, iterator

            try:
                with lock:
                    item = next(iterator)

            except StopIteration:
                observer.close()
            else:
                observer.send(item)
                mad.disposable = scheduler.schedule_relative(delay, action)

        mad.disposable = scheduler.schedule_relative(delay, action)
        return mad
    return AnonymousObservable(subscribe)
