from rx import Lock
from rx.core import Observable, AnonymousObservable
from rx.concurrency import current_thread_scheduler
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable, alias=["from_", "from_list"])
def from_iterable(cls, iterable, scheduler=None):
    """Converts an array to an observable sequence, using an optional
    scheduler to enumerate the array.

    1 - res = rx.Observable.from_iterable([1,2,3])
    2 - res = rx.Observable.from_iterable([1,2,3], rx.Scheduler.timeout)

    Keyword arguments:
    :param Observable cls: Observable class
    :param Scheduler scheduler: [Optional] Scheduler to run the
        enumeration of the input sequence on.

    :returns: The observable sequence whose elements are pulled from the
        given enumerable sequence.
    :rtype: Observable
    """

    scheduler = scheduler or current_thread_scheduler
    lock = Lock()

    def subscribe(observer):
        iterator = iter(iterable)

        def action(action1, state=None):
            try:
                with lock:
                    item = next(iterator)
            except StopIteration:
                observer.on_completed()
            else:
                observer.on_next(item)
                action1(action)

        return scheduler.schedule_recursive(action)
    return AnonymousObservable(subscribe)
