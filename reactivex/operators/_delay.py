from datetime import datetime
from typing import Any, Callable, List, Optional, TypeVar

from reactivex import Notification, Observable, abc
from reactivex import operators as ops
from reactivex import typing
from reactivex.disposable import (
    CompositeDisposable,
    MultipleAssignmentDisposable,
    SerialDisposable,
)
from reactivex.internal.constants import DELTA_ZERO
from reactivex.notification import OnError
from reactivex.scheduler import TimeoutScheduler

from ._timestamp import Timestamp

_T = TypeVar("_T")


def observable_delay_timespan(
    source: Observable[_T],
    duetime: typing.RelativeTime,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Observable[_T]:
    def subscribe(
        observer: abc.ObserverBase[_T], scheduler_: Optional[abc.SchedulerBase] = None
    ):
        nonlocal duetime

        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

        if isinstance(duetime, datetime):
            duetime_ = _scheduler.to_datetime(duetime) - _scheduler.now
        else:
            duetime_ = _scheduler.to_timedelta(duetime)

        cancelable = SerialDisposable()
        exception: Optional[Exception] = None
        active = [False]
        running = [False]
        queue: List[Timestamp[Notification[_T]]] = []

        def on_next(notification: Timestamp[Notification[_T]]) -> None:
            nonlocal exception
            should_run = False

            with source.lock:
                if isinstance(notification.value, OnError):
                    del queue[:]
                    queue.append(notification)
                    exception = notification.value.exception
                    should_run = not running[0]
                else:
                    queue.append(
                        Timestamp(
                            value=notification.value,
                            timestamp=notification.timestamp + duetime_,
                        )
                    )
                    should_run = not active[0]
                    active[0] = True

            if should_run:
                if exception:
                    observer.on_error(exception)
                else:
                    mad = MultipleAssignmentDisposable()
                    cancelable.disposable = mad

                    def action(scheduler: abc.SchedulerBase, state: Any = None):
                        if exception:
                            return

                        with source.lock:
                            running[0] = True
                            while True:
                                result = None
                                if queue and queue[0].timestamp <= scheduler.now:
                                    result = queue.pop(0).value

                                if result:
                                    result.accept(observer)

                                if not result:
                                    break

                            should_continue = False
                            recurse_duetime: typing.RelativeTime = 0
                            if queue:
                                should_continue = True
                                diff = queue[0].timestamp - scheduler.now
                                recurse_duetime = max(DELTA_ZERO, diff)
                            else:
                                active[0] = False

                            ex = exception
                            running[0] = False

                        if ex:
                            observer.on_error(ex)
                        elif should_continue:
                            mad.disposable = scheduler.schedule_relative(
                                recurse_duetime, action
                            )

                    mad.disposable = _scheduler.schedule_relative(duetime_, action)

        subscription = source.pipe(
            ops.materialize(),
            ops.timestamp(),
        ).subscribe(on_next, scheduler=_scheduler)

        return CompositeDisposable(subscription, cancelable)

    return Observable(subscribe)


def delay_(
    duetime: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    def delay(source: Observable[_T]) -> Observable[_T]:
        """Time shifts the observable sequence.

        A partially applied delay operator function.

        Examples:
            >>> res = delay(source)

        Args:
            source: The observable sequence to delay.

        Returns:
            A time-shifted observable sequence.
        """
        return observable_delay_timespan(source, duetime, scheduler)

    return delay


__all__ = ["delay_"]
