from typing import Callable, Optional

from rx.core import Observable, typing
from rx.disposable import CompositeDisposable
from rx.scheduler import TimeoutScheduler


def _take_with_time(duration: typing.RelativeTime, scheduler: Optional[typing.Scheduler] = None
                    ) -> Callable[[Observable], Observable]:
    def take_with_time(source: Observable) -> Observable:
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

        def subscribe(observer, scheduler_=None):
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

            def action(scheduler, state):
                observer.on_completed()

            disp = _scheduler.schedule_relative(duration, action)
            return CompositeDisposable(disp, source.subscribe(observer, scheduler=scheduler_))
        return Observable(subscribe)
    return take_with_time
