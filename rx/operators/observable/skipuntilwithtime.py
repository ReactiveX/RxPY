from datetime import datetime

from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.internal import extensionmethod
from rx.concurrency import timeout_scheduler


@extensionmethod(Observable)
def skip_until_with_time(self, start_time):
    """Skips elements from the observable source sequence until the
    specified start time.
    Errors produced by the source sequence are always forwarded to the
    result sequence, even if the error occurs before the start time.

    Examples:
    res = source.skip_until_with_time(new Date());
    res = source.skip_until_with_time(5000);

    Keyword arguments:
    start_time -- Time to start taking elements from the source sequence. If
        this value is less than or equal to Date(), no elements will be
        skipped.

    Returns an observable sequence with the elements skipped
    until the specified start time.
    """


    source = self

    if isinstance(start_time, datetime):
        scheduler_method = 'schedule_absolute'
    else:
        scheduler_method = 'schedule_relative'

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or timeout_scheduler
        open = [False]

        def send(x):
            if open[0]:
                observer.send(x)
        subscription = source.subscribe_callbacks(send, observer.throw, observer.close, scheduler)

        def action(scheduler, state):
            open[0] = True
        disposable = getattr(scheduler, scheduler_method)(start_time, action)
        return CompositeDisposable(disposable, subscription)
    return AnonymousObservable(subscribe)
