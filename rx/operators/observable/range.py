from rx.core import Observable, AnonymousObservable
from rx.concurrency import current_thread_scheduler
from rx.disposables import MultipleAssignmentDisposable


def from_range(start: int, stop: int = None, step: int = None) -> Observable:
    """Generates an observable sequence of integral numbers within a
    specified range, using the specified scheduler to send out observer
    messages.

    1 - res = Rx.Observable.range(10)
    2 - res = Rx.Observable.range(0, 10)
    3 - res = Rx.Observable.range(0, 10, 1)

    Keyword arguments:
    start -- The value of the first integer in the sequence.
    count -- The number of sequential integers to generate.
    scheduler -- [Optional] Scheduler to run the generator loop on. If not
        specified, defaults to Scheduler.current_thread.

    Returns an observable sequence that contains a range of sequential
    integral numbers.
    """

    if step is None and stop is None:
        range_t = range(start)
    elif step is None:
        range_t = range(start, stop)
    else:
        range_t = range(start, stop, step)

    def subscribe(observer, scheduler=None):
        nonlocal range_t

        scheduler = scheduler or current_thread_scheduler
        sd = MultipleAssignmentDisposable()

        def action(scheduler, iterator):
            try:
                observer.send(next(iterator))
                sd.disposable = scheduler.schedule(action, state=iterator)
            except StopIteration:
                observer.close()

        sd.disposable = scheduler.schedule(action, iter(range_t))
        return sd
    return AnonymousObservable(subscribe)
