from rx.observable import Observable
from rx.concurrency import TimeoutScheduler, timeout_scheduler, Scheduler
from rx.internal import extends

@extends(Observable)
class Interval(object):


    @classmethod
    def interval(cls, period, scheduler=None):
        """Returns an observable sequence that produces a value after each
        period.

        Example:
        1 - res = rx.Observable.interval(1000)
        2 - res = rx.Observable.interval(1000, rx.Scheduler.timeout)

        Keyword arguments:
        period -- Period for producing the values in the resulting sequence
            (specified as an integer denoting milliseconds).
        scheduler -- [Optional] Scheduler to run the timer on. If not specified,
            rx.Scheduler.timeout is used.

        Returns an observable sequence that produces a value after each period.
        """

        scheduler = scheduler or TimeoutScheduler()
        return Observable.observable_timer_timespan_and_period(period, period, scheduler)
