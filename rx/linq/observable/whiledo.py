from six import add_metaclass
from itertools import takewhile

from rx.observable import Observable

from rx.internal.enumerable import Enumerable
from rx.concurrency import current_thread_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableWhileDo(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
   
    @classmethod
    def while_do(cls, condition, source):
        """Repeats source as long as condition holds emulating a while loop.
        
        Keyword arguments:
        condition -- {Function} The condition which determines if the source 
            will be repeated.
        source -- {Observable} The observable sequence that will be run if the 
            condition function returns true.
   
        Returns an observable {Observable} sequence which is repeated as long 
        as the condition holds."""
        
        source = Observable.from_future(source)
        return Observable.concat(Enumerable.while_do(condition, source))    
