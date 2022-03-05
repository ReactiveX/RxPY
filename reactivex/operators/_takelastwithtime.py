from typing import Any, Callable, Dict, List, Optional, TypeVar

from reactivex import Observable, abc, typing
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


def take_last_with_time_(
    duration: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    def take_last_with_time(source: Observable[_T]) -> Observable[_T]:
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

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler_: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            nonlocal duration

            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
            duration = _scheduler.to_timedelta(duration)
            q: List[Dict[str, Any]] = []

            def on_next(x: _T) -> None:
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

            return source.subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler_
            )

        return Observable(subscribe)

    return take_last_with_time


__all__ = ["take_last_with_time_"]
