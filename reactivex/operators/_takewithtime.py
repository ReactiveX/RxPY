from typing import Any, TypeVar

from reactivex import Observable, abc, typing
from reactivex.disposable import CompositeDisposable
from reactivex.internal import curry_flip
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


@curry_flip
def take_with_time_(
    source: Observable[_T],
    duration: typing.RelativeTime,
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[_T]:
    """Takes elements for the specified duration from the start of
    the observable source sequence.

    Examples:
        >>> source.pipe(take_with_time(5.0))
        >>> take_with_time(5.0)(source)

    This operator accumulates a queue with a length enough to store
    elements received during the initial duration window. As more
    elements are received, elements older than the specified
    duration are taken from the queue and produced on the result
    sequence. This causes elements to be delayed with duration.

    Args:
        source: Source observable to take elements from.
        duration: Duration for taking elements from the start of
            the sequence.
        scheduler: Scheduler to use for timing.

    Returns:
        An observable sequence with the elements taken during the
        specified duration from the start of the source sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler_: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

        def action(scheduler: abc.SchedulerBase, state: Any = None):
            observer.on_completed()

        disp = _scheduler.schedule_relative(duration, action)
        return CompositeDisposable(
            disp, source.subscribe(observer, scheduler=scheduler_)
        )

    return Observable(subscribe)


__all__ = ["take_with_time_"]
