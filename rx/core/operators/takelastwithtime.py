from typing import Callable, Optional
from rx.core import Observable, typing
from rx.scheduler import TimeoutScheduler


def _take_last_with_time(duration: typing.RelativeTime, scheduler: Optional[typing.Scheduler] = None
                         ) -> Callable[[Observable], Observable]:
    def take_last_with_time(source: Observable) -> Observable:
        """Returns elements within the specified duration from the end
        of the observable source sequence.

        Example:
            >>> res = take_last_with_time(source)

        This operator accumulates a queue with a length enough to store
        elements received during the initial duration window. As more
        elements are received, elements older than the specified
        duration are taken from the queue and produced on the result
        sequence. This causes elements to be delayed with duration.

        Args:
            duration: Duration for taking elements from the end of the
            sequence.

        Returns:
            An observable sequence with the elements taken during the
            specified duration from the end of the source sequence.
        """
        def subscribe(observer, scheduler_=None):
            nonlocal duration

            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
            duration = _scheduler.to_timedelta(duration)
            q = []

            def on_next(x):
                now = _scheduler.now
                q.append({"interval": now, "value": x})
                while q and now - q[0]["interval"] >= duration:
                    q.pop(0)

            def on_completed():
                now = _scheduler.now
                while q:
                    _next = q.pop(0)
                    if now - _next["interval"] <= duration:
                        observer.on_next(_next["value"])

                observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, on_completed, scheduler_)
        return Observable(subscribe)
    return take_last_with_time
