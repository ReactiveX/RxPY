from typing import Callable

from rx import operators as ops
from rx.core import Observable, AnonymousObservable
from rx.internal.utils import TimeInterval
from rx.concurrency import timeout_scheduler


def _time_interval() -> Callable[[Observable], Observable]:
    def time_interval(source: Observable) -> Observable:
        """Records the time interval between consecutive values in an
        observable sequence.

            >>> res = time_interval(source)

        Return:
            An observable sequence with time interval information on
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

            return source.pipe(ops.map(mapper)).subscribe(observer, scheduler)
        return AnonymousObservable(subscribe)
    return time_interval