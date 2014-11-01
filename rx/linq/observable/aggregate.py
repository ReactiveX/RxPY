from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod

class ObservableAggregate(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def aggregate(self, accumulator, seed=None):
        """Applies an accumulator function over an observable sequence, 
        returning the result of the aggregation as a single element in the 
        result sequence. The specified seed value is used as the initial 
        accumulator value.
     
        For aggregation behavior with incremental intermediate results, see 
        Observable.scan.
     
        Example:
        1 - res = source.aggregate(lambda acc, x: acc + x)
        2 - res = source.aggregate(lambda acc, x: acc + x, seed=0)

        Keyword arguments:
        accumulator -- An accumulator function to be invoked on each element.
        seed -- [Optional] The initial accumulator value.
        
        Returns an observable sequence containing a single element with the 
        final accumulator value."""

        if not seed is None:
            return self.scan(accumulator, seed=seed).start_with(seed).final_value()
        else:
            return self.scan(accumulator).final_value()
    
Observable.aggregate = ObservableAggregate.aggregate