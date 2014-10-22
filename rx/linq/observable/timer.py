import logging
from datetime import datetime
from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable
from rx.concurrency import timeout_scheduler, Scheduler
from rx.internal import ExtensionMethod

log = logging.getLogger("Rx")

# Rx Utils
class TimeInterval(object):
    def __init__(self, value, interval):
        self.value = value
        self.interval = interval

class Timestamp(object):
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

@add_metaclass(ExtensionMethod)
class ObservableTimer(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def observable_timer_timespan_and_period(cls, duetime, period, scheduler):
        if duetime == period:
            def subscribe(observer):
                def action(count):
                    observer.on_next(count)
                    count += 1
                    return count

                return scheduler.schedule_periodic(period, action, 0)
            return AnonymousObservable(subscribe)

        def deferred():
            return cls.observable_timer_date_and_period(scheduler.now() + duetime, period, scheduler)
        return Observable.defer(deferred)

    @staticmethod
    def observable_timer_date(duetime, scheduler):
        def subscribe(observer):
            def action(scheduler, state):
                observer.on_next(0)
                observer.on_completed()

            return scheduler.schedule_absolute(duetime, action)
        return AnonymousObservable(subscribe)

    @staticmethod
    def observable_timer_date_and_period(duetime, period, scheduler):
        p = Scheduler.normalize(period)

        def subscribe(observer):
            count = [0]
            d = [duetime]

            def action(scheduler, state):
                if p > 0:
                    now = scheduler.now()
                    d[0] = d[0] + p
                    if d[0] <= now:
                        d[0] = now + p

                observer.on_next(count[0])
                count[0] += 1
                state(d[0])

            return scheduler.schedule_recursive(d, action)
        return AnonymousObservable(subscribe)

    @staticmethod
    def observable_timer_timespan(duetime, scheduler):
        d = Scheduler.normalize(duetime)

        def subscribe(observer):
            def action(scheduler, state):
                observer.on_next(0)
                observer.on_completed()

            return scheduler.schedule_relative(d, action)
        return AnonymousObservable(subscribe)

    @classmethod
    def observable_timer_timespan_and_period(cls, duetime, period, scheduler):
        if duetime == period:
            def subscribe(observer):
                def action(count):
                    observer.on_next(count)
                    return count + 1

                return scheduler.schedule_periodic(period, action, state=0)
            return AnonymousObservable(subscribe)

        def defer():
            return cls.observable_timer_date_and_period(scheduler.now() + duetime, period, scheduler)
        return Observable.defer(defer)

    @classmethod
    def timer(cls, duetime, period=None, scheduler=None):
        """Returns an observable sequence that produces a value after duetime
        has elapsed and then after each period.

        1 - res = Observable.timer(datetime(...))
        2 - res = Observable.timer(datetime(...), 1000)
        3 - res = Observable.timer(datetime(...), Scheduler.timeout)
        4 - res = Observable.timer(datetime(...), 1000, Scheduler.timeout)

        5 - res = Observable.timer(5000)
        6 - res = Observable.timer(5000, 1000)
        7 - res = Observable.timer(5000, scheduler=Scheduler.timeout)
        8 - res = Observable.timer(5000, 1000, Scheduler.timeout)

        Keyword arguments:
        duetime -- Absolute (specified as a Date object) or relative time
            (specified as an integer denoting milliseconds) at which to produce
            the first value.</param>
        period -- [Optional] Period to produce subsequent values (specified as
            an integer denoting milliseconds), or the scheduler to run the
            timer on. If not specified, the resulting timer is not recurring.
        scheduler -- [Optional] Scheduler to run the timer on. If not
            specified, the timeout scheduler is used.

        Returns an observable sequence that produces a value after due time has
        elapsed and then each period.
        """
        log.debug("Observable.timer(duetime=%s, period=%s)", duetime, period)

        scheduler = scheduler or timeout_scheduler

        if isinstance(duetime, datetime) and period is None:
            return cls.observable_timer_date(duetime, scheduler)

        if isinstance(duetime, datetime) and period:
            return cls.observable_timer_date_and_period(duetime, period, scheduler)

        if period is None:
            return cls.observable_timer_timespan(duetime, scheduler)

        return cls.observable_timer_timespan_and_period(duetime, period, scheduler)
