import six

from rx.concurrency import Scheduler
from rx.observable import Observable, ObservableMeta

from rx.concurrency import immediate_scheduler
#from rx.linq.enumerable import Enumerable

@six.add_metaclass(ObservableMeta)
class ObservableStartsWith(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
    
    def start_with(self, *args, **kw):
        """Prepends a sequence of values to an observable sequence with an 
        optional scheduler and an argument list of values to prepend.
        
        1 - source.start_with(1, 2, 3)
        2 - source.start_with(Scheduler.timeout, 1, 2, 3)
        
        Returns the source sequence prepended with the specified values.
        """
        
        scheduler = kw.get("scheduler")
        
        if not scheduler and isinstance(args[0], Scheduler):
            scheduler = args[0]
            args = args[1:]
        else:
            scheduler = immediate_scheduler

        sequence = [Observable.from_array(args, scheduler), self]
        return Observable.concat(sequence)
        #return Observable.concat(Enumerable.for_each(sequence))
