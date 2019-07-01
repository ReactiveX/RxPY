from asyncio import Future
from datetime import datetime
from typing import cast, Callable, Optional, Union

from rx import from_future, throw
from rx.core import Observable, typing
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.scheduler import TimeoutScheduler
from rx.internal.utils import is_future


def _timeout(duetime: typing.AbsoluteTime,
             other: Optional[Union[Observable, Future]] = None,
             scheduler: Optional[typing.Scheduler] = None
             ) -> Callable[[Observable], Observable]:

    other = other or throw(Exception("Timeout"))
    if is_future(other):
        obs = from_future(cast(Future, other))
    else:
        obs = cast(Observable, other)

    def timeout(source: Observable) -> Observable:
        """Returns the source observable sequence or the other observable
        sequence if duetime elapses.

        Examples:
            >>> res = timeout(source)

        Args:
            source: Source observable to timeout

        Returns:
            An obserable sequence switching to the other sequence in
            case of a timeout.
        """
        def subscribe(observer, scheduler_=None):
            _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()

            if isinstance(duetime, datetime):
                scheduler_method = _scheduler.schedule_absolute
            else:
                scheduler_method = _scheduler.schedule_relative

            switched = [False]
            _id = [0]

            original = SingleAssignmentDisposable()
            subscription = SerialDisposable()
            timer = SerialDisposable()
            subscription.disposable = original

            def create_timer():
                my_id = _id[0]

                def action(scheduler, state=None):
                    switched[0] = (_id[0] == my_id)
                    timer_wins = switched[0]
                    if timer_wins:
                        subscription.disposable = obs.subscribe(observer, scheduler=scheduler)

                timer.disposable = scheduler_method(duetime, action)

            create_timer()

            def on_next(value):
                send_wins = not switched[0]
                if send_wins:
                    _id[0] += 1
                    observer.on_next(value)
                    create_timer()

            def on_error(error):
                on_error_wins = not switched[0]
                if on_error_wins:
                    _id[0] += 1
                    observer.on_error(error)

            def on_completed():
                on_completed_wins = not switched[0]
                if on_completed_wins:
                    _id[0] += 1
                    observer.on_completed()

            original.disposable = source.subscribe_(on_next, on_error, on_completed, scheduler_)
            return CompositeDisposable(subscription, timer)
        return Observable(subscribe)
    return timeout
