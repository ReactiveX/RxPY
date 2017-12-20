from rx.core import ObservableBase, AnonymousObservable
from rx.internal.utils import TimeInterval
from rx.concurrency import timeout_scheduler


def time_interval(source: ObservableBase) -> ObservableBase:
    """Records the time interval between consecutive values in an
    observable sequence.

    1 - res = time_interval(source)

    Return An observable sequence with time interval information on
    values.
    """

    def subscribe(observer, scheduler):
        scheduler = scheduler or timeout_scheduler
        last = scheduler.now

        def selector(value):
            nonlocal last

            now = scheduler.now
            span = now - last
            last = now
            return TimeInterval(value=value, interval=span)

        return source.map(selector).subscribe(observer, scheduler)
    return AnonymousObservable(subscribe)
