import logging
from datetime import datetime

from rx.core import ObservableBase, AnonymousObservable
from rx.disposables import MultipleAssignmentDisposable

log = logging.getLogger("Rx")


def observable_timer_date(duetime):
    def subscribe(observer, scheduler=None):
        def action(scheduler, state):
            observer.on_next(0)
            observer.on_completed()

        return scheduler.schedule_absolute(duetime, action)
    return AnonymousObservable(subscribe)


def observable_timer_duetime_and_period(duetime, period) -> ObservableBase:
    def subscribe(observer, scheduler=None):
        nonlocal duetime

        if isinstance(duetime, int):
            duetime = scheduler.now + scheduler.to_timedelta(duetime)

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

            observer.on_next(count[0])
            count[0] += 1
            mad.disposable = scheduler.schedule_absolute(dt[0], action)
        mad.disposable = scheduler.schedule_absolute(dt[0], action)
        return mad
    return AnonymousObservable(subscribe)


def observable_timer_timespan(duetime) -> ObservableBase:

    def subscribe(observer, scheduler=None):
        d = scheduler.normalize(duetime)

        def action(scheduler, state):
            observer.on_next(0)
            observer.on_completed()

        return scheduler.schedule_relative(d, action)
    return AnonymousObservable(subscribe)


def observable_timer_timespan_and_period(duetime, period) -> ObservableBase:
    if duetime == period:
        def subscribe(observer, scheduler=None):
            def action(count):
                observer.on_next(count)
                return count + 1

            return scheduler.schedule_periodic(period, action, state=0)
        return AnonymousObservable(subscribe)
    return observable_timer_duetime_and_period(duetime, period)


def timer(duetime, period=None) -> ObservableBase:
    """Returns an observable sequence that produces a value after duetime
    has elapsed and then after each period.

    1 - res = Observable.timer(datetime(...))
    2 - res = Observable.timer(datetime(...), 1000)

    5 - res = Observable.timer(5000)
    6 - res = Observable.timer(5000, 1000)

    Keyword arguments:
    duetime -- Absolute (specified as a datetime object) or relative time
        (specified as an integer denoting milliseconds) at which to produce
        the first value.</param>
    period -- [Optional] Period to produce subsequent values (specified as
        an integer denoting milliseconds), or the scheduler to run the
        timer on. If not specified, the resulting timer is not recurring.

    Returns an observable sequence that produces a value after due time has
    elapsed and then each period.
    """

    log.debug("Observable.timer(duetime=%s, period=%s)", duetime, period)

    if isinstance(duetime, datetime):
        if period is None:
            return observable_timer_date(duetime)
        else:
            return observable_timer_duetime_and_period(duetime, period)

    if period is None:
        return observable_timer_timespan(duetime)

    return observable_timer_timespan_and_period(duetime, period)
