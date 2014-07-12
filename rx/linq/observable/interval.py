from six import add_metaclass

from rx.observable import Observable, ObservableMeta
from rx.concurrency import TimeoutScheduler, timeout_scheduler, Scheduler

@add_metaclass(ObservableMeta)
class ObservableInterval(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
    
    @classmethod
    def interval(cls, period, scheduler=None):
        """Returns an observable sequence that produces a value after each period.
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
        return cls.observable_timer_timespan_and_period(period, period, scheduler)
