from rx import Observable, AnonymousObservable
from rx.observable import ObservableMeta
from rx.internal.basic import default_key_serializer, identity
from rx.internal import ArgumentOutOfRangeException

class ObservableSkip(Observable, metaclass=ObservableMeta):
    """Note that we do some magic here by using a meta class to extend 
    Observable with the methods in this class"""
    
    def skip(self, count):
        """Bypasses a specified number of elements in an observable sequence 
        and then returns the remaining elements.
        
        Keyword arguments:
        count -- The number of elements to skip before returning the remaining 
            elements.
        
        Returns an observable sequence that contains the elements that occur 
        after the specified index in the input sequence.
        """        
        
        if count < 0:
            raise ArgumentOutOfRangeException()
        
        observable = self

        def subscribe(observer):
            remaining = count

            def on_next(value):
                nonlocal remaining

                if remaining <= 0:
                    observer.on_next(value)
                else:
                    remaining -= 1
                
            return observable.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)
