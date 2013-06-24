from rx import AnonymousObservable, Observable
from rx.observable import ObservableMeta
from rx.observeonobserver import ObserveOnObserver
from rx.disposables import SingleAssignmentDisposable, SerialDisposable, ScheduledDisposable

class ObservableAggregates(Observable, metaclass=ObservableMeta):

    def aggregate(self, accumulator, seed=None):
        """Applies an accumulator function over an observable sequence, 
        returning the result of the aggregation as a single element in the 
        result sequence. The specified seed value is used as the initial 
        accumulator value.
     
        For aggregation behavior with incremental intermediate results, see 
        Observable.scan.
     
        1 - res = source.aggregate(function (acc, x) { return acc + x; });
        2 - res = source.aggregate(0, function (acc, x) { return acc + x; });

        Keyword arguments:
        accumulator -- An accumulator function to be invoked on each element.
        seed -- [Optional] The initial accumulator value.
        
        Returns an observable sequence containing a single element with the 
        final accumulator value.
        """

        if seed:
            return self.scan(seed, accumulator).start_with(seed).final_value()
        else:
            return self.scan(accumulator).final_value()
    
    def reduce(self, accumulator, seed=None):
        if seed: 
            return self.scan(seed, accumulator).start_with(seed).final_value()
        else:
            return self.scan(accumulator).final_value()
    
    def count(self, predicate=None):
        """Returns an observable sequence containing a value that represents 
        how many elements in the specified observable sequence satisfy a 
        condition if provided, else the count of items.
     
        1 - res = source.count()
        2 - res = source.count(lambda x: x > 3)
    
        Keyword arguments:
        predicate -- [Optional] A function to test each element for a condition.
     
        Returns an observable sequence containing a single element with a 
        number that represents how many elements in the input sequence satisfy 
        the condition in the predicate function if provided, else the count of 
        items in the sequence.
        """

        if predicate:
            return self.where(predicate).count()
        else:
            return self.aggregate(seed=0, accumulator=lambda count: count + 1)