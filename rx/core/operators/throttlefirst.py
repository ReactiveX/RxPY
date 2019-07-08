from typing import Callable, Optional

from rx.core import Observable, typing
from rx.scheduler import TimeoutScheduler


def _throttle_first(window_duration: typing.RelativeTime, scheduler: Optional[typing.Scheduler] = None
                   ) -> Callable[[Observable], Observable]:
    def throttle_first(source: Observable) -> Observable:
        """Returns an observable that emits only the first item emitted
        by the source Observable during sequential time windows of a
        specifiedduration.

        Args:
            source: Source observable to throttle.

        Returns:
            An Observable that performs the throttle operation.
        """
        def subscribe(observer, scheduler_=None):
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

            duration = _scheduler.to_timedelta(window_duration or 0.0)
            if duration <= _scheduler.to_timedelta(0):
                raise ValueError('window_duration cannot be less or equal zero.')
            last_on_next = [0]

            def on_next(x):
                emit = False
                now = _scheduler.now

                with source.lock:
                    if not last_on_next[0] or now - last_on_next[0] >= duration:
                        last_on_next[0] = now
                        emit = True
                if emit:
                    observer.on_next(x)

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler=_scheduler)
        return Observable(subscribe)
    return throttle_first
