
from rx.internal import Enumerable
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable

from .observable_single import concat

class ObservableMultiple(Observable, metaclass=ObservableMeta):
    def __init__(self, subscribe):
        self.concat = self.__concat # Stitch in instance method

    def merge_observable(self):
        """Merges an observable sequence of observable sequences into an 
        observable sequence.
        
        Returns the observable sequence that merges the elements of the inner 
        sequences.        
        """
        sources = self

        def subscribe(observer):
            m = SingleAssignmentDisposable()
            group = CompositeDisposable()
            is_stopped = False
            group.add(m)
            
            def on_next(inner_source):
                inner_subscription = SingleAssignmentDisposable()
                group.add(inner_subscription)

                def on_complete():
                    nonlocal group
                    
                    group.remove(inner_subscription)
                    if is_stopped and group.length == 1:
                        observer.on_completed()
                    
                disposable = inner_source.subscribe(
                    observer.on_next,
                    observer.on_error, 
                    on_complete)
                
                inner_subscription.disposable = disposable
            
            def on_complete():
                nonlocal is_stopped

                is_stopped = True
                if group.length == 1:
                    observer.on_completed()
            
            m.disposable = sources.subscribe(on_next, observer.on_error, on_complete)
            return group
        
        return AnonymousObservable(subscribe)

    def __concat(self, *args):
        """Concatenates all the observable sequences. This takes in either an 
        array or variable arguments to concatenate.
     
        1 - concatenated = xs.concat(ys, zs)
        2 - concatenated = xs.concat([ys, zs])
     
        Returns an observable sequence that contains the elements of each given
        sequence, in sequential order. 
        """
        
        if isinstance(args[0], list):
            items = args[0]
        else:
            items = list(args)
        return Observable.concat(items)
    
    @classmethod
    def concat(cls, *args):
        """Concatenates all the observable sequences.
    
        1 - res = Rx.Observable.concat(xs, ys, zs);
        2 - res = Rx.Observable.concat([xs, ys, zs]);
     
        Returns an observable sequence that contains the elements of each given
        sequence, in sequential order.
        """
        
        if isinstance(args[0], list):
            sources = args[0]
        else:
            sources = list(args)
        
        return concat(Enumerable.for_each(sources))

    def concat_all(self):
        """Concatenates an observable sequence of observable sequences.
        
        Returns an observable sequence that contains the elements of each 
        observed inner sequence, in sequential order.
        """
        return self.merge(1)
    

