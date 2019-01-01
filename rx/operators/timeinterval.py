from rx.core import Observable, AnonymousObservable
from rx.internal.utils import TimeInterval
from rx.concurrency import timeout_scheduler


def time_interval(source: Observable) -> Observable:
    """Records the time interval between consecutive values in an
    observable sequence.

    1 - res = time_interval(source)

    Return An observable sequence with time interval information on
    values.
    """

    def subscribe(observer, scheduler):
        scheduler = scheduler or timeout_scheduler
        last = scheduler.now

        def mapper(value):
            nonlocal last

            now = scheduler.now
            span = now - last
            last = now
            return TimeInterval(value=value, interval=span)

        return source.map(mapper).subscribe(observer, scheduler)
    return AnonymousObservable(subscribe)
