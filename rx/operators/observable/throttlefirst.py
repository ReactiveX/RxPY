from datetime import timedelta
from typing import Union

from rx.core import ObservableBase, AnonymousObservable
from rx.concurrency import timeout_scheduler


def throttle_first(source, window_duration: Union[timedelta, int]) -> ObservableBase:
    """Returns an Observable that emits only the first item emitted by
    the source Observable during sequential time windows of a specified
    duration.

    Keyword arguments:
    window_duration -- time to wait before emitting another item after
        emitting the last item.
    Returns an Observable that performs the throttle operation.
    """

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or timeout_scheduler

        duration = scheduler.to_timedelta(+window_duration or 0)
        if duration <= scheduler.to_timedelta(0):
            raise ValueError('window_duration cannot be less or equal zero.')
        last_on_next = [0]

        def on_next(x):
            emit = False
            now = scheduler.now

            with source.lock:
                if not last_on_next[0] or now - last_on_next[0] >= duration:
                    last_on_next[0] = now
                    emit = True
            if emit:
                observer.on_next(x)

        return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler=scheduler)
    return AnonymousObservable(subscribe)
