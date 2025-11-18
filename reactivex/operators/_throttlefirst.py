from datetime import datetime
from typing import TypeVar

from reactivex import Observable, abc, typing
from reactivex.internal import curry_flip
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


@curry_flip
def throttle_first_(
    source: Observable[_T],
    window_duration: typing.RelativeTime,
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[_T]:
    """Returns an observable that emits only the first item emitted
    by the source Observable during sequential time windows of a
    specified duration.

    Examples:
        >>> result = source.pipe(throttle_first(1.0))
        >>> result = throttle_first(1.0)(source)

    Args:
        source: Source observable to throttle.
        window_duration: Duration of windows during which to throttle.
        scheduler: Optional scheduler to use for timing.

    Returns:
        An Observable that performs the throttle operation.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler_: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

        duration = _scheduler.to_timedelta(window_duration or 0.0)
        if duration <= _scheduler.to_timedelta(0):
            raise ValueError("window_duration cannot be less or equal zero.")
        last_on_next: datetime | None = None

        def on_next(x: _T) -> None:
            nonlocal last_on_next
            emit = False
            now = _scheduler.now

            with source.lock:
                if not last_on_next or now - last_on_next >= duration:
                    last_on_next = now
                    emit = True
            if emit:
                observer.on_next(x)

        return source.subscribe(
            on_next, observer.on_error, observer.on_completed, scheduler=_scheduler
        )

    return Observable(subscribe)


__all__ = ["throttle_first_"]
