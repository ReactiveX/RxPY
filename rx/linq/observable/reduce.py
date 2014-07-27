from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableReduce(Observable):    
    """Uses a meta class to extend Observable with the methods in this class"""

    def reduce(self, accumulator, seed=None):
        if not seed is None: 
            return self.scan(accumulator, seed=seed).start_with(seed).final_value()
        else:
            return self.scan(accumulator).final_value()
    
    