from six import add_metaclass
from rx import AnonymousObservable, Observable
from rx.observable import ObservableMeta
from rx.observeonobserver import ObserveOnObserver
from rx.disposables import SingleAssignmentDisposable, SerialDisposable, ScheduledDisposable

@add_metaclass(ObservableMeta)
class ObservableAggregates(Observable):

    def aggregate(self, accumulator, seed=None):
        """Applies an accumulator function over an observable sequence, 
        returning the result of the aggregation as a single element in the 
        result sequence. The specified seed value is used as the initial 
        accumulator value.
     
        For aggregation behavior with incremental intermediate results, see 
        Observable.scan.
     
        1 - res = source.aggregate(lambda acc, x: acc + x)
        2 - res = source.aggregate(0, lambda acc, x: acc + x, seed=0)

        Keyword arguments:
        accumulator -- An accumulator function to be invoked on each element.
        seed -- [Optional] The initial accumulator value.
        
        Returns an observable sequence containing a single element with the 
        final accumulator value.
        """

        if not seed is None:
            return self.scan(accumulator, seed=seed).start_with(seed).final_value()
        else:
            return self.scan(accumulator).final_value()
    
    def reduce(self, accumulator, seed=None):
        if not seed is None: 
            return self.scan(accumulator, seed=seed).start_with(seed).final_value()
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
            return self.aggregate(lambda count, _: count + 1, seed=0)