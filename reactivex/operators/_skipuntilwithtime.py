from datetime import datetime
from typing import Any, Callable, Optional, TypeVar

from reactivex import Observable, abc, typing
from reactivex.disposable import CompositeDisposable
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


def skip_until_with_time_(
    start_time: typing.AbsoluteOrRelativeTime,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    def skip_until_with_time(source: Observable[_T]) -> Observable[_T]:
        """Skips elements from the observable source sequence until the
        specified start time.

        Errors produced by the source sequence are always forwarded to
        the result sequence, even if the error occurs before the start
        time.

        Examples:
            >>> res = source.skip_until_with_time(datetime)
            >>> res = source.skip_until_with_time(5.0)

        Args:
            start_time: Time to start taking elements from the source
                sequence. If this value is less than or equal to
                `datetime.utcnow`, no elements will be skipped.

        Returns:
            An observable sequence with the elements skipped until the
            specified start time.
        """

        if isinstance(start_time, datetime):
            scheduler_method = "schedule_absolute"
        else:
            scheduler_method = "schedule_relative"

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler_: Optional[abc.SchedulerBase] = None,
        ):
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

            open = [False]

            def on_next(x: _T) -> None:
                if open[0]:
                    observer.on_next(x)

            subscription = source.subscribe(
                on_next, observer.on_error, observer.on_completed, scheduler=scheduler_
            )

            def action(scheduler: abc.SchedulerBase, state: Any):
                open[0] = True

            disp = getattr(_scheduler, scheduler_method)(start_time, action)
            return CompositeDisposable(disp, subscription)

        return Observable(subscribe)

    return skip_until_with_time


__all__ = ["skip_until_with_time_"]
