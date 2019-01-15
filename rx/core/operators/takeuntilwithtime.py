from typing import Callable, Union
from datetime import datetime

from rx.core import Observable, AnonymousObservable, typing
from rx.disposables import CompositeDisposable
from rx.concurrency import timeout_scheduler


def _take_until_with_time(end_time: Union[datetime, int], scheduler: typing.Scheduler
                          ) -> Callable[[Observable], Observable]:
    def take_until_with_time(source: Observable) -> Observable:
        """Takes elements for the specified duration until the specified end
        time, using the specified scheduler to run timers.

        Examples:
            >>> res = source.take_until_with_time(dt, [optional scheduler])
            >>> res = source.take_until_with_time(5000, [optional scheduler])

        Args:
            source: Source observale to take elements from.

        Returns:
            An observable sequence with the elements taken
            until the specified end time.
        """

        def subscribe(observer, scheduler_=None):
            _scheduler = scheduler or scheduler_ or timeout_scheduler

            if isinstance(end_time, datetime):
                scheduler_method = _scheduler.schedule_absolute
            else:
                scheduler_method = _scheduler.schedule_relative

            def action(scheduler, state):
                observer.on_completed()

            task = scheduler_method(end_time, action)
            return CompositeDisposable(task, source.subscribe(observer, scheduler_))
        return AnonymousObservable(subscribe)
    return take_until_with_time
