import logging
from datetime import datetime

from rx.core import Observable, AnonymousObservable
from rx.concurrency import timeout_scheduler
from rx.disposables import MultipleAssignmentDisposable
from rx.internal import extensionclassmethod

log = logging.getLogger("Rx")


def observable_timer_date(duetime):
    def subscribe(observer, scheduler=None):
        def action(scheduler, state):
            observer.send(0)
            observer.close()

        return scheduler.schedule_absolute(duetime, action)
    return AnonymousObservable(subscribe)


def observable_timer_date_and_period(duetime, period):
    def subscribe(observer, scheduler=None):
        p = scheduler.normalize(period)
        mad = MultipleAssignmentDisposable()
        dt = [duetime]
        count = [0]

        def action(scheduler, state):
            if p > 0:
                now = scheduler.now
                dt[0] = dt[0] + scheduler.to_timedelta(p)
                if dt[0] <= now:
                    dt[0] = now + scheduler.to_timedelta(p)

            observer.send(count[0])
            count[0] += 1
            mad.disposable = scheduler.schedule_absolute(dt[0], action)
        mad.disposable = scheduler.schedule_absolute(dt[0], action)
        return mad
    return AnonymousObservable(subscribe)


def observable_timer_timespan(duetime):

    def subscribe(observer, scheduler=None):
        d = scheduler.normalize(duetime)

        def action(scheduler, state):
            observer.send(0)
            observer.close()

        return scheduler.schedule_relative(d, action)
    return AnonymousObservable(subscribe)


def observable_timer_timespan_and_period(duetime, period):
    if duetime == period:
        def subscribe(observer, scheduler=None):
            def action(count):
                observer.send(count)
                return count + 1

            return scheduler.schedule_periodic(period, action, state=0)
        return AnonymousObservable(subscribe)

    def defer():
        dt = scheduler.now + scheduler.to_timedelta(duetime)
        return observable_timer_date_and_period(dt, period, scheduler)
    return Observable.defer(defer)


@extensionclassmethod(Observable)
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
        return observable_timer_date(duetime)

    if isinstance(duetime, datetime) and period:
        return observable_timer_date_and_period(duetime, period)

    if period is None:
        return observable_timer_timespan(duetime)

    return observable_timer_timespan_and_period(duetime, period)
