from typing import Callable, Optional
from datetime import datetime

from rx.core import Observable, typing
from rx.disposable import CompositeDisposable
from rx.scheduler import TimeoutScheduler
from rx.internal.utils import subscribe as _subscribe


def _take_until_with_time(end_time: typing.AbsoluteOrRelativeTime,
                          scheduler: Optional[typing.Scheduler] = None
                          ) -> Callable[[Observable], Observable]:
    def take_until_with_time(source: Observable) -> Observable:
        """Takes elements for the specified duration until the specified end
        time, using the specified scheduler to run timers.

        Examples:
            >>> res = take_until_with_time(source)

        Args:
            source: Source observale to take elements from.

        Returns:
            An observable sequence with the elements taken
            until the specified end time.
        """

        def subscribe_observer(observer: typing.Observer,
                               scheduler_: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

            if isinstance(end_time, datetime):
                scheduler_method = _scheduler.schedule_absolute
            else:
                scheduler_method = _scheduler.schedule_relative

            def action(scheduler, state):
                observer.on_completed()

            task = scheduler_method(end_time, action)
            sub = _subscribe(source, observer, scheduler=scheduler_)
            return CompositeDisposable(task, sub)
        return Observable(subscribe_observer=subscribe_observer)
    return take_until_with_time
