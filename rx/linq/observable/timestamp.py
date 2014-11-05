from rx.observable import Observable
from rx.concurrency import current_thread_scheduler

class Timestamp(object):
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

class ObservableTimestamp:
    """Uses a meta class to extend Observable with the methods in this class"""

    def timestamp(self, scheduler=None):
        """Records the timestamp for each value in an observable sequence.
      
        1 - res = source.timestamp() # produces { value: x, timestamp: ts }
        2 - res = source.timestamp(rx.Scheduler.timeout)
       
        scheduler -- [Optional] Scheduler used to compute timestamps. If not 
            specified, the timeout scheduler is used.
    
        Returns an observable sequence with timestamp information on values.
        """

        scheduler = scheduler or timeout_scheduler

        def selector(x):
            return Timestamp(value=x, timestamp=scheduler.now())

        return self.select(selector)

Observable.timestamp = ObservableTimestamp.timestamp