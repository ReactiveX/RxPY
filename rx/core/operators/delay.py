from typing import Callable, Optional
from datetime import datetime, timedelta

from rx import operators as ops
from rx.core import Observable, typing
from rx.internal.constants import DELTA_ZERO
from rx.disposable import CompositeDisposable, SerialDisposable, MultipleAssignmentDisposable
from rx.scheduler import TimeoutScheduler


class Timestamp(object):
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp


def observable_delay_timespan(source: Observable, duetime: typing.RelativeTime,
                              scheduler: Optional[typing.Scheduler] = None) -> Observable:

    def subscribe(observer, scheduler_=None):
        nonlocal duetime

        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

        if isinstance(duetime, datetime):
            duetime = _scheduler.to_datetime(duetime) - _scheduler.now
        else:
            duetime = _scheduler.to_timedelta(duetime)

        cancelable = SerialDisposable()
        exception = [None]
        active = [False]
        running = [False]
        queue = []

        def on_next(notification):
            should_run = False

            with source.lock:
                if notification.value.kind == 'E':
                    del queue[:]
                    queue.append(notification)
                    exception[0] = notification.value.exception
                    should_run = not running[0]
                else:
                    queue.append(Timestamp(value=notification.value, timestamp=notification.timestamp + duetime))
                    should_run = not active[0]
                    active[0] = True

            if should_run:
                if exception[0]:
                    observer.on_error(exception[0])
                else:
                    mad = MultipleAssignmentDisposable()
                    cancelable.disposable = mad

                    def action(scheduler, state):
                        if exception[0]:
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
                            recurse_duetime = 0
                            if queue:
                                should_continue = True
                                diff = queue[0].timestamp - scheduler.now
                                zero = DELTA_ZERO if isinstance(diff, timedelta) else 0
                                recurse_duetime = max(zero, diff)
                            else:
                                active[0] = False

                            ex = exception[0]
                            running[0] = False

                        if ex:
                            observer.on_error(ex)
                        elif should_continue:
                            mad.disposable = scheduler.schedule_relative(recurse_duetime, action)

                    mad.disposable = _scheduler.schedule_relative(duetime, action)
        subscription = source.pipe(
            ops.materialize(),
            ops.timestamp()
        ).subscribe_(on_next, scheduler=scheduler_)

        return CompositeDisposable(subscription, cancelable)
    return Observable(subscribe)


def _delay(duetime: typing.RelativeTime, scheduler: Optional[typing.Scheduler] = None) -> Callable[[Observable], Observable]:
    def delay(source: Observable) -> Observable:
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
