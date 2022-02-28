from typing import Any, Callable, Optional, TypeVar

from reactivex import Observable, abc, typing
from reactivex.disposable import CompositeDisposable
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


def take_with_time_(
    duration: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    def take_with_time(source: Observable[_T]) -> Observable[_T]:
        """Takes elements for the specified duration from the start of
        the observable source sequence.

        Example:
            >>> res = take_with_time(source)

        This operator accumulates a queue with a length enough to store
        elements received during the initial duration window. As more
        elements are received, elements older than the specified
        duration are taken from the queue and produced on the result
        sequence. This causes elements to be delayed with duration.

        Args:
            source: Source observable to take elements from.

        Returns:
            An observable sequence with the elements taken during the
            specified duration from the start of the source sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler_: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

            def action(scheduler: abc.SchedulerBase, state: Any = None):
                observer.on_completed()

            disp = _scheduler.schedule_relative(duration, action)
            return CompositeDisposable(
                disp, source.subscribe(observer, scheduler=scheduler_)
            )

        return Observable(subscribe)

    return take_with_time


__all__ = ["take_with_time_"]
