from typing import Any, Callable, Optional, TypeVar

from reactivex import Observable, abc, typing
from reactivex.disposable import CompositeDisposable
from reactivex.scheduler import TimeoutScheduler

_T = TypeVar("_T")


def skip_with_time_(
    duration: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    def skip_with_time(source: Observable[_T]) -> Observable[_T]:
        """Skips elements for the specified duration from the start of
        the observable source sequence.

        Args:
            >>> res = skip_with_time(5.0)

        Specifying a zero value for duration doesn't guarantee no
        elements will be dropped from the start of the source sequence.
        This is a side-effect of the asynchrony introduced by the
        scheduler, where the action that causes callbacks from the
        source sequence to be forwarded may not execute immediately,
        despite the zero due time.

        Errors produced by the source sequence are always forwarded to
        the result sequence, even if the error occurs before the
        duration.

        Args:
            duration: Duration for skipping elements from the start of
            the sequence.

        Returns:
            An observable sequence with the elements skipped during the
            specified duration from the start of the source sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler_: Optional[abc.SchedulerBase] = None,
        ):
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
            open = [False]

            def action(scheduler: abc.SchedulerBase, state: Any) -> None:
                open[0] = True

            t = _scheduler.schedule_relative(duration, action)

            def on_next(x: _T):
                if open[0]:
                    observer.on_next(x)

            d = source.subscribe(
                on_next, observer.on_error, observer.on_completed, scheduler=scheduler_
            )
            return CompositeDisposable(t, d)

        return Observable(subscribe)

    return skip_with_time


__all__ = ["skip_with_time_"]
