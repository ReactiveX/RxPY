from datetime import datetime
from typing import Union

from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import timeout_scheduler


def timeout(source, duetime: Union[int, datetime], other: Observable = None) -> Observable:
    """Returns the source observable sequence or the other observable
    sequence if duetime elapses.

    1 - res = source.timeout(5000); # 5 seconds
    # As a date and timeout observable
    2 - res = source.timeout(datetime(), Observable.return_value(42))
    # 5 seconds and timeout observable
    3 - res = source.timeout(5000, Observable.return_value(42))
    # As a date and timeout observable

    Keyword arguments:
    duetime -- Absolute (specified as a datetime object) or relative
        time (specified as an integer denoting milliseconds) when a
        timeout occurs.
    other -- Sequence to return in case of a timeout. If not
        specified, a timeout error throwing sequence will be used.

    Returns the source sequence switching to the other sequence in case
        of a timeout.
    """

    other = other or Observable.throw_exception(Exception("Timeout"))
    other = Observable.from_future(other)

    def subscribe(observer, scheduler=None):
        scheduler = scheduler or timeout_scheduler

        if isinstance(duetime, datetime):
            scheduler_method = scheduler.schedule_absolute
        else:
            scheduler_method = scheduler.schedule_relative

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
        def send(value):
            send_wins = not switched[0]
            if send_wins:
                _id[0] += 1
                observer.send(value)
                create_timer()

        def throw(error):
            throw_wins = not switched[0]
            if throw_wins:
                _id[0] += 1
                observer.throw(error)

        def close():
            close_wins = not switched[0]
            if close_wins:
                _id[0] += 1
                observer.close()

        original.disposable = source.subscribe_callbacks(send, throw, close, scheduler)
        return CompositeDisposable(subscription, timer)
    return AnonymousObservable(subscribe)
