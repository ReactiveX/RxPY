from datetime import datetime
from typing import Union, Callable

from rx import from_future, throw
from rx.core import Observable, AnonymousObservable, typing
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import timeout_scheduler
from rx.internal.utils import is_future


def _timeout(duetime: typing.AbsoluteTime, other: Observable = None, scheduler: typing.Scheduler = None
             ) -> Callable[[Observable], Observable]:

    other = other or throw(Exception("Timeout"))
    other = from_future(other) if is_future(other) else other

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
            _scheduler = scheduler or scheduler_ or timeout_scheduler

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
                        subscription.disposable = other.subscribe(observer, scheduler)

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
        return AnonymousObservable(subscribe)
    return timeout
