from typing import Union
from datetime import timedelta

from rx.core import ObservableBase, AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.concurrency import timeout_scheduler

def skip_with_time(source: ObservableBase, duration: Union[timedelta, int]) -> ObservableBase:
    """Skips elements for the specified duration from the start of the
    observable source sequence.

    Example:
    1 - res = source.skip_with_time(5000)

    Description:
    Specifying a zero value for duration doesn't guarantee no elements
    will be dropped from the start of the source sequence. This is a
    side-effect of the asynchrony introduced by the scheduler, where the
    action that causes callbacks from the source sequence to be
    forwarded may not execute immediately, despite the zero due time.

    Errors produced by the source sequence are always forwarded to the
    result sequence, even if the error occurs before the duration.

    Keyword arguments:
    duration -- Duration for skipping elements from the start of the
        sequence.

    Returns an observable sequence with the elements skipped during the
    specified duration from the start of the source sequence.
    """

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or timeout_scheduler
        open = [False]

        def action(scheduler, state):
            open[0] = True

        t = scheduler.schedule_relative(duration, action)

        def send(x):
            if open[0]:
                observer.send(x)

        d = source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
        return CompositeDisposable(t, d)
    return AnonymousObservable(subscribe)

