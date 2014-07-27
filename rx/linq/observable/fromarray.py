from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.concurrency import current_thread_scheduler
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableCreation(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
    
    @classmethod
    def from_array(cls, array, scheduler=None):
        """Converts an array to an observable sequence, using an optional 
        scheduler to enumerate the array.
    
        1 - res = rx.Observable.from_array([1,2,3])
        2 - res = rx.Observable.from_array([1,2,3], rx.Scheduler.timeout)
     
        Keyword arguments:
        scheduler -- [Optional] Scheduler to run the enumeration of the input
            sequence on.
     
        Returns the observable sequence whose elements are pulled from the 
        given enumerable sequence.
        """

        scheduler = scheduler or current_thread_scheduler

        def subscribe(observer):
            count = [0]
            
            def action(action1, state=None):
                if count[0] < len(array):
                    observer.on_next(array[count[0]])
                    count[0] += 1
                    action1(action)
                else:
                    observer.on_completed()
                
            return scheduler.schedule_recursive(action)
        return AnonymousObservable(subscribe)
