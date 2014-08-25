import logging
from datetime import datetime, timedelta
from six import add_metaclass

from rx.internal.utils import add_ref
from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.subjects import Subject
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable, RefCountDisposable
from rx.concurrency import timeout_scheduler
from rx.internal import ExtensionMethod

log = logging.getLogger("Rx")

# Rx Utils
class TimeInterval(object):
    def __init__(self, value, interval):
        self.value = value
        self.interval = interval

    #def __str__(self):
    #    return "%s@%s" % (self.value, self.interval)

    #def equals(other):
    #    return other.interval == self.interval and other.value == self.value


class Timestamp(object):
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

    #def __str__(self):
    #    return "%s@%s" % (self.value, self.timestamp)

    #def equals(other):
    #    return other.timestamp == self.timestamp and other.value == self.value

@add_metaclass(ExtensionMethod)
class ObservableTime(Observable):

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


    @classmethod
    def generate_with_relative_time(cls, initial_state, condition, iterate, result_selector, time_selector, scheduler=None):
        """Generates an observable sequence by iterating a state from an
        initial state until the condition fails.
        
        res = source.generate_with_relative_time(0, 
            lambda x: True, 
            lambda x: x + 1, 
            lambda x: x, 
            lambda x: 500)
    
        initial_state -- Initial state.
        condition -- Condition to terminate generation (upon returning false).
        iterate -- Iteration step function.
        result_selector -- Selector function for results produced in the
            sequence.
        time_selector -- Time selector function to control the speed of values
            being produced each iteration, returning integer values denoting
            milliseconds.
        scheduler -- [Optional] Scheduler on which to run the generator loop.
            If not specified, the timeout scheduler is used.

        Returns the generated sequence.
        """
        scheduler = scheduler or timeout_scheduler

        def subscribe(observer):
            state = [initial_state]
            has_result = [False]
            result = [None]
            first = [True]
            time = None

            def action(this):
                if has_result[0]:
                    observer.on_next(result[0])

                try:
                    if first[0]:
                        first[0] = False
                    else:
                        state[0] = iterate(state[0])

                    has_result[0] = condition(state[0])
                    if has_result[0]:
                        result[0] = result_selector(state[0])
                        time = time_selector(state[0])

                except Exception as e:
                    observer.on_error(e)
                    return

                if has_result[0]:
                    this(time)
                else:
                    observer.on_completed()

            return scheduler.schedule_recursive_with_relative(0, action)
        return AnonymousObservable(subscribe)

