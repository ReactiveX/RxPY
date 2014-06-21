from rx import AnonymousObservable, Observable
from rx.observable import ObservableMeta

class ObservableAll(Observable, metaclass=ObservableMeta):
    def scan(self, accumulator, seed=None):
        """Applies an accumulator function over an observable sequence and 
        returns each intermediate result. The optional seed value is used as 
        the initial accumulator value. For aggregation behavior with no 
        intermediate results, see Observable.aggregate.
        
        1 - scanned = source.scan(lambda acc, x: acc + x)
        2 - scanned = source.scan(0, lambda acc, x: acc + x)
        
        Keyword arguments:
        seed -- [Optional] The initial accumulator value.
        accumulator -- An accumulator function to be invoked on each element.
        
        Returns an observable sequence containing the accumulated values.        
        """
        has_seed = False
        if not seed is None:
            has_seed = True

        source = self

        def defer():
            has_accumulation = False
            accumulation = None

            def projection(x):
                nonlocal accumulation, has_accumulation

                if has_accumulation:
                    accumulation = accumulator(accumulation, x)
                else:
                    accumulation =  accumulator(seed, x) if has_seed else x
                    has_accumulation = True
                
                return accumulation
            return source.select(projection)
        return Observable.defer(defer)
