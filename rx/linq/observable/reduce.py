from rx import AnonymousObservable, Observable
from rx.observable import ObservableMeta

class ObservableReduce(Observable, metaclass=ObservableMeta):    
    def reduce(self, accumulator, seed=None):
        if not seed is None: 
            return self.scan(accumulator, seed=seed).start_with(seed).final_value()
        else:
            return self.scan(accumulator).final_value()
    
    