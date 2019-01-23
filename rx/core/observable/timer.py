from datetime import datetime

from rx.core import Observable, AnonymousObservable, typing
from rx.disposable import MultipleAssignmentDisposable


def observable_timer_date(duetime, scheduler: typing.Scheduler = None):
    def subscribe(observer, scheduler_=None):
        _scheduler = scheduler or scheduler_

        def action(scheduler, state):
            observer.on_next(0)
            observer.on_completed()

        return _scheduler.schedule_absolute(duetime, action)
    return AnonymousObservable(subscribe)


def observable_timer_duetime_and_period(duetime, period, scheduler: typing.Scheduler = None) -> Observable:
    def subscribe(observer, scheduler_=None):
        _scheduler = scheduler or scheduler_
        nonlocal duetime

        if not isinstance(duetime, datetime):
            duetime = _scheduler.now + _scheduler.to_timedelta(duetime)

        p = _scheduler.normalize(period)
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
        mad.disposable = _scheduler.schedule_absolute(dt[0], action)
        return mad
    return AnonymousObservable(subscribe)


def observable_timer_timespan(duetime: typing.RelativeTime, scheduler: typing.Scheduler = None) -> Observable:
    def subscribe(observer, scheduler_=None):
        _scheduler = scheduler or scheduler_
        d = _scheduler.normalize(duetime)

        def action(scheduler, state):
            observer.on_next(0)
            observer.on_completed()

        return _scheduler.schedule_relative(d, action)
    return AnonymousObservable(subscribe)


def observable_timer_timespan_and_period(duetime: typing.RelativeTime, period: typing.RelativeTime,
                                         scheduler: typing.Scheduler = None) -> Observable:
    if duetime == period:
        def subscribe(observer, scheduler_=None):
            _scheduler = scheduler or scheduler_

            def action(count):
                observer.on_next(count)
                return count + 1

            return _scheduler.schedule_periodic(period, action, state=0)
        return AnonymousObservable(subscribe)
    return observable_timer_duetime_and_period(duetime, period, scheduler)


def _timer(duetime: typing.AbsoluteOrRelativeTime, period: typing.RelativeTime = None,
           scheduler: typing.Scheduler = None) -> Observable:
    if isinstance(duetime, datetime):
        if period is None:
            return observable_timer_date(duetime, scheduler)
        else:
            return observable_timer_duetime_and_period(duetime, period, scheduler)

    if period is None:
        return observable_timer_timespan(duetime, scheduler)

    return observable_timer_timespan_and_period(duetime, period, scheduler)
