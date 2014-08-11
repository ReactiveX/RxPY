from six import add_metaclass

from rx import Observable, AnonymousObservable
from rx.internal.basic import default_key_serializer, identity
from rx.internal import ArgumentOutOfRangeException
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableSkip(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""
    
    def skip_last(self, count):
        """Bypasses a specified number of elements at the end of an observable 
        sequence.
        
        Description:
        This operator accumulates a queue with a length enough to store the 
        first `count` elements. As more elements are received, elements are 
        taken from the front of the queue and produced on the result sequence. 
        This causes elements to be delayed.     
        
        Keyword arguments
        count -- Number of elements to bypass at the end of the source sequence.
        
        Returns an observable {Observable} sequence containing the source 
        sequence elements except for the bypassed ones at the end."""
        
        source = self

        def subscribe(observer):
            q = []
            
            def on_next(x):
                q.append(x)
                if len(q) > count:
                    observer.on_next(q.pop(0))
    
            return source.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)

