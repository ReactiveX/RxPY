from six import add_metaclass
from itertools import takewhile

from rx.observable import Observable

from rx.internal.enumerable import Enumerable
from rx.concurrency import current_thread_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableDoWhile(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
   
    def do_while(self, condition):
        """Repeats source as long as condition holds emulating a do while loop.
        
        Keyword arguments:
        condition -- {Function} The condition which determines if the source 
            will be repeated.
        
        Returns an observable {Observable} sequence which is repeated as long 
        as the condition holds."""
 
        return Observable.concat([self, Observable.while_do(condition, self)])
