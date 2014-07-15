import logging
from six import add_metaclass

from rx.observable import Observable, ObservableMeta
from rx.concurrency import timeout_scheduler

log = logging.getLogger("Rx")

class Timestamp(object):
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

@add_metaclass(ObservableMeta)
class ObservableTimestamp(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def timestamp(self, scheduler=None):
        """Records the timestamp for each value in an observable sequence.
      
        1 - res = source.timestamp(); // produces { value: x, timestamp: ts }
        2 - res = source.timestamp(Rx.Scheduler.timeout);
       
        scheduler -- [Optional] Scheduler used to compute timestamps. If not 
            specified, the timeout scheduler is used.
    
        Returns an observable sequence with timestamp information on values.
        """
        scheduler = scheduler or timeout_scheduler

        def selector(x):
            return Timestamp(value=x, timestamp=scheduler.now())

        return self.select(selector)
