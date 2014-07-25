from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableAny(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def any(self, predicate=None, this=None):
        """Determines whether any element of an observable sequence satisfies a
        condition if present, else if any items are in the sequence.
        
        Example:
        result = source.any()
        result = source.any(lambda x: x > 3)

        predicate -- A function to test each element for a condition.
     
        Returns {Observable} an observable sequence containing a single element
        determining whether any elements in the source sequence pass the test 
        in the specified predicate if given, else if any items are in the 
        sequence."""
    
        source = self
        def subscribe(observer):
            def on_next(_):
                observer.on_next(True)
                observer.on_completed()
            def on_error():
                observer.on_next(False)
                observer.on_completed()
            return source.subscribe(on_next, observer.on_error, on_error)

        return source.where(predicate, this).any() if predicate else AnonymousObservable(subscribe)
            
    some = any
