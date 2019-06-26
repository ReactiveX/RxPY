from datetime import datetime
from typing import Callable, Optional

from rx.core import Observable, typing
from rx.disposable import CompositeDisposable
from rx.scheduler import TimeoutScheduler


def _skip_until_with_time(start_time: typing.AbsoluteOrRelativeTime, scheduler: Optional[typing.Scheduler] = None
                          ) -> Callable[[Observable], Observable]:
    def skip_until_with_time(source: Observable) -> Observable:
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
            scheduler_method = 'schedule_absolute'
        else:
            scheduler_method = 'schedule_relative'

        def subscribe(observer, scheduler_=None):
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

            open = [False]

            def on_next(x):
                if open[0]:
                    observer.on_next(x)
            subscription = source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler_)

            def action(scheduler, state):
                open[0] = True
            disp = getattr(_scheduler, scheduler_method)(start_time, action)
            return CompositeDisposable(disp, subscription)
        return Observable(subscribe)
    return skip_until_with_time
