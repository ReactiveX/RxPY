from datetime import datetime
from typing import Any, Optional

from reactivex import Observable, abc, typing
from reactivex.disposable import MultipleAssignmentDisposable
from reactivex.scheduler import TimeoutScheduler
from reactivex.scheduler.periodicscheduler import PeriodicScheduler


def observable_timer_date(
    duetime: typing.AbsoluteTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Observable[int]:
    def subscribe(
        observer: abc.ObserverBase[int], scheduler_: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        _scheduler: abc.SchedulerBase = (
            scheduler or scheduler_ or TimeoutScheduler.singleton()
        )

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            observer.on_next(0)
            observer.on_completed()

        return _scheduler.schedule_absolute(duetime, action)

    return Observable(subscribe)


def observable_timer_duetime_and_period(
    duetime: typing.AbsoluteOrRelativeTime,
    period: typing.AbsoluteOrRelativeTime,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Observable[int]:
    def subscribe(
        observer: abc.ObserverBase[int], scheduler_: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
        nonlocal duetime

        if not isinstance(duetime, datetime):
            duetime = _scheduler.now + _scheduler.to_timedelta(duetime)

        p = max(0.0, _scheduler.to_seconds(period))
        mad = MultipleAssignmentDisposable()
        dt = duetime
        count = 0

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            nonlocal dt
            nonlocal count

            if p > 0.0:
                now = scheduler.now
                dt = dt + scheduler.to_timedelta(p)
                if dt <= now:
                    dt = now + scheduler.to_timedelta(p)

            observer.on_next(count)
            count += 1
            mad.disposable = scheduler.schedule_absolute(dt, action)

        mad.disposable = _scheduler.schedule_absolute(dt, action)
        return mad

    return Observable(subscribe)


def observable_timer_timespan(
    duetime: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Observable[int]:
    def subscribe(
        observer: abc.ObserverBase[int], scheduler_: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        _scheduler = scheduler or scheduler_ or TimeoutScheduler.singleton()
        d = _scheduler.to_seconds(duetime)

        def action(scheduler: abc.SchedulerBase, state: Any) -> None:
            observer.on_next(0)
            observer.on_completed()

        if d <= 0.0:
            return _scheduler.schedule(action)
        return _scheduler.schedule_relative(d, action)

    return Observable(subscribe)


def observable_timer_timespan_and_period(
    duetime: typing.RelativeTime,
    period: typing.RelativeTime,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Observable[int]:
    if duetime == period:

        def subscribe(
            observer: abc.ObserverBase[int],
            scheduler_: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            _scheduler: abc.SchedulerBase = (
                scheduler or scheduler_ or TimeoutScheduler.singleton()
            )

            def action(count: Optional[int] = None) -> Optional[int]:
                if count is not None:
                    observer.on_next(count)
                    return count + 1
                return None

            if not isinstance(_scheduler, PeriodicScheduler):
                raise ValueError("Sceduler must be PeriodicScheduler")
            return _scheduler.schedule_periodic(period, action, state=0)

        return Observable(subscribe)
    return observable_timer_duetime_and_period(duetime, period, scheduler)


def timer_(
    duetime: typing.AbsoluteOrRelativeTime,
    period: Optional[typing.RelativeTime] = None,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Observable[int]:
    if isinstance(duetime, datetime):
        if period is None:
            return observable_timer_date(duetime, scheduler)
        else:
            return observable_timer_duetime_and_period(duetime, period, scheduler)

    if period is None:
        return observable_timer_timespan(duetime, scheduler)

    return observable_timer_timespan_and_period(duetime, period, scheduler)


__all__ = ["timer_"]
