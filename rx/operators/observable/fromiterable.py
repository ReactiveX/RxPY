from typing import Iterable
from rx.core.bases.scheduler import Scheduler
from rx import config
from rx.core import Observable, AnonymousObservable
from rx.concurrency import current_thread_scheduler
from rx.disposables import MultipleAssignmentDisposable


def from_iterable(iterable: Iterable) -> Observable:
    """Converts an array to an observable sequence, using an optional
    scheduler to enumerate the array.

    1 - res = rx.Observable.from_iterable([1,2,3])

    Returns the observable sequence whose elements are pulled from the
        given enumerable sequence.
    """

    lock = config["concurrency"].RLock()

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or current_thread_scheduler

        sd = MultipleAssignmentDisposable()
        iterator = iter(iterable)

        def action(scheduler, state=None):
            nonlocal observer, sd, iterator

            try:
                with lock:
                    item = next(iterator)

            except StopIteration:
                observer.close()
            else:
                observer.send(item)
                sd.disposable = scheduler.schedule(action)

        sd.disposable = scheduler.schedule(action)
        return sd
    return AnonymousObservable(subscribe)
