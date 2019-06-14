from typing import Callable, NamedTuple, Any, Optional
from datetime import timedelta


from rx import operators as ops
from rx.core import Observable, typing
from rx.scheduler import TimeoutScheduler
from rx.internal.utils import subscribe as _subscribe


class TimeInterval(NamedTuple):
    value: Any
    interval: timedelta


def _time_interval(scheduler: Optional[typing.Scheduler] = None
                   ) -> Callable[[Observable], Observable]:
    def time_interval(source: Observable) -> Observable:
        """Records the time interval between consecutive values in an
        observable sequence.

            >>> res = time_interval(source)

        Return:
            An observable sequence with time interval information on
            values.
        """

        def subscribe_observer(observer: typing.Observer,
                               scheduler_: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
            last = _scheduler.now

            def mapper(value):
                nonlocal last

                now = _scheduler.now
                span = now - last
                last = now
                return TimeInterval(value=value, interval=span)

            return _subscribe(source.pipe(ops.map(mapper)),
                              observer,
                              scheduler=scheduler_)
        return Observable(subscribe_observer=subscribe_observer)
    return time_interval
