from six import add_metaclass
from rx.observable import Observable, ObservableMeta

from rx.concurrency import current_thread_scheduler

@add_metaclass(ObservableMeta)
class ObservableRepeat(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
    
    @classmethod
    def repeat(cls, value=None, repeat_count=None, scheduler=None):
        """Generates an observable sequence that repeats the given element the 
        specified number of times, using the specified scheduler to send out 
        observer messages.
    
        1 - res = Rx.Observable.repeat(42)
        2 - res = Rx.Observable.repeat(42, 4)
        3 - res = Rx.Observable.repeat(42, 4, Rx.Scheduler.timeout)
        4 - res = Rx.Observable.repeat(42, None, Rx.Scheduler.timeout)
    
        Keyword arguments:
        value -- Element to repeat.
        repeat_count -- [Optiona] Number of times to repeat the element. If not 
            specified, repeats indefinitely.
        scheduler -- Scheduler to run the producer loop on. If not specified, 
            defaults to ImmediateScheduler.
    
        Returns an observable sequence that repeats the given element the 
        specified number of times.
        """

        scheduler = scheduler or current_thread_scheduler
        if repeat_count == -1:
            repeat_count = None
        
        xs = cls.return_value(value, scheduler)
        ret = xs.repeat(repeat_count)
        return ret
