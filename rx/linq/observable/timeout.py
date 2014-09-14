from datetime import datetime, timedelta

from six import add_metaclass

from rx.internal import noop
from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableTimer(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def timeout(self, duetime, other=None, scheduler=None):
        """
        Returns the source observable sequence or the other observable sequence
        if duetime elapses.

        1 - res = source.timeout(new Date()); # As a date
        2 - res = source.timeout(5000); # 5 seconds
        3 - res = source.timeout(datetime(), rx.Observable.return_value(42)) # As a date and timeout observable
        4 - res = source.timeout(5000, rx.Observable.return_value(42)) # 5 seconds and timeout observable
        5 - res = source.timeout(datetime(), rx.Observable.return_value(42), 
                                 rx.Scheduler.timeout) # As a date and timeout observable
        6 - res = source.timeout(5000, rx.Observable.return_value(42), 
                                 rx.Scheduler.timeout) # 5 seconds and timeout observable

        duetime -- Absolute (specified as a datetime object) or relative time
            (specified as an integer denoting milliseconds) when a timeout
            occurs.
        other -- [Optional] Sequence to return in case of a timeout. If not
            specified, a timeout error throwing sequence will be used.
        scheduler -- [Optional] Scheduler to run the timeout timers on. If not
            specified, the timeout scheduler is used.

        Returns the source sequence switching to the other sequence in case of
        a timeout.
        """

        scheduler_method = None
        source = self

        other = other or Observable.throw_exception(Exception("Timeout"))
        other = Observable.from_future(other)
        
        scheduler = scheduler or timeout_scheduler

        if isinstance(duetime, datetime):
            scheduler_method = scheduler.schedule_absolute
        else:
            scheduler_method = scheduler.schedule_relative

        def subscribe(observer):
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
                        
                        subscription.disposable = other.subscribe(observer)

                timer.disposable = scheduler_method(duetime, action)

            create_timer()
            def on_next(x):
                on_next_wins = not switched[0]
                if on_next_wins:
                    _id[0] += 1
                    observer.on_next(x)
                    create_timer()

            def on_error(e):
                on_error_wins = not switched[0]
                if on_error_wins:
                    _id[0] += 1
                    observer.on_error(e)

            def on_completed():
                on_completed_wins = not switched[0]
                if on_completed_wins:
                    _id[0] += 1
                    observer.on_completed()

            original.disposable = source.subscribe(on_next, on_error, on_completed)
            return CompositeDisposable(subscription, timer)
        return AnonymousObservable(subscribe)
