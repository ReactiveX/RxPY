from rx import Observable, AnonymousObservable
from rx.observable import ObservableMeta
from rx.internal.utils import adapt_call

class ObservableSkip(Observable, metaclass=ObservableMeta):
    """Note that we do some magic here by using a meta class to extend 
    Observable with the methods in this class"""
    
    def skip_while(self, predicate):
        """Bypasses elements in an observable sequence as long as a specified 
        condition is true and then returns the remaining elements. The 
        element's index is used in the logic of the predicate function.
        
        1 - source.skip_while(lambda value: value < 10)
        2 - source.skip_while(lambda value, index: value < 10 or index < 10)
        
        predicate -- A function to test each element for a condition; the 
            second parameter of the function represents the index of the 
            source element.
        
        Returns an observable sequence that contains the elements from the 
        input sequence starting at the first element in the linear series that
        does not pass the test specified by predicate.        
        """
        predicate = adapt_call(predicate)
        source = self

        def subscribe(observer):
            i, running = 0, False

            def on_next(value):
                nonlocal running, i
                if not running:
                    try:
                        running = not predicate(value, i)
                    except Exception as exn:
                        observer.on_error(exn)
                        return
                    else:
                        i += 1
        
                if running:
                    observer.on_next(value)
                
            return source.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)
