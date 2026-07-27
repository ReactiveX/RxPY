from typing import Any, TypeVar

from reactivex import Observable, abc, typing
from reactivex.internal import curry_flip
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


@curry_flip
def take_last_with_time_(
    source: Observable[_T],
    duration: typing.RelativeTime,
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[_T]:
    """Returns elements within the specified duration from the end
    of the observable source sequence.

    Examples:
        >>> source.pipe(take_last_with_time(5.0))
        >>> take_last_with_time(5.0)(source)

    This operator accumulates a queue with a length enough to store
    elements received during the initial duration window. As more
    elements are received, elements older than the specified
    duration are taken from the queue and produced on the result
    sequence. This causes elements to be delayed with duration.

    Args:
        source: Source observable to take elements from.
        duration: Duration for taking elements from the end of the
            sequence.
        scheduler: Scheduler to use for timing.

    Returns:
        An observable sequence with the elements taken during the
        specified duration from the end of the source sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler_: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        nonlocal duration

        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
        duration = _scheduler.to_timedelta(duration)
        q: list[dict[str, Any]] = []

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


__all__ = ["take_last_with_time_"]
