from rx import AnonymousObservable, Observable
from rx.observable import ObservableMeta

class ObservableAll(Observable, metaclass=ObservableMeta):
    def all(self, predicate, this=None):
        """Determines whether all elements of an observable sequence satisfy a
        condition.
        
        1 - res = source.all(lambda value: value.length > 3)
        
        predicate -- A function to test each element for a condition.
        this -- Object to use as self when executing callback.
        
        Returns an observable sequence containing a single element determining 
        whether all elements in the source sequence pass the test in the 
        specified predicate."""
    
        return self.where(lambda v: not predicate(v), this).any().select(lambda b: not b)
        
    every = all
