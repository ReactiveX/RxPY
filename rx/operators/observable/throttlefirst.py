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
        last_send = [0]

        def send(x):
            emit = False
            now = scheduler.now

            with source.lock:
                if not last_send[0] or now - last_send[0] >= duration:
                    last_send[0] = now
                    emit = True
            if emit:
                observer.send(x)

        return source.subscribe_(send, observer.throw, observer.close, scheduler=scheduler)
    return AnonymousObservable(subscribe)
