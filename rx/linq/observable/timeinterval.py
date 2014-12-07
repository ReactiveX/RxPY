from rx.observable import Observable
from rx.concurrency import timeout_scheduler
from rx.internal import extends

# Rx Utils
class TimeInterval(object):
    def __init__(self, value, interval):
        self.value = value
        self.interval = interval

class Timestamp(object):
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

@extends(Observable)
class TimeInteval(object):


    def time_interval(self, scheduler):
        """Records the time interval between consecutive values in an
        observable sequence.

        1 - res = source.time_interval();
        2 - res = source.time_interval(Scheduler.timeout)

        Keyword arguments:
        scheduler -- [Optional] Scheduler used to compute time intervals. If
            not specified, the timeout scheduler is used.

        Return An observable sequence with time interval information on values.
        """

        source = self
        scheduler = scheduler or timeout_scheduler

        def defer():
            last = [scheduler.now()]

            def selector(x):
                now = scheduler.now()
                span = now - last[0]
                last[0] = now
                return TimeInterval(value=x, interval=span)

            return source.select(selector)
        return Observable.defer(defer)


