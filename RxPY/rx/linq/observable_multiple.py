
from rx.internal import Enumerable, noop
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

    def switch(self):
        """Transforms an observable sequence of observable sequences into an 
        observable sequence producing values only from the most recent 
        observable sequence.
        
        Returns the observable sequence that at any point in time produces the 
        elements of the most recent inner observable sequence that has been received.  
        """
    
        sources = self

        def subscribe(observer):
            has_latest = False
            inner_subscription = SerialDisposable()
            is_stopped = False
            latest = 0

            def on_next(inner_source):
                nonlocal latest, has_latest

                d = SingleAssignmentDisposable()
                latest += 1
                _id = latest
                has_latest = True
                inner_subscription.disposable = d

                def on_next(x):
                    if latest == _id:
                        observer.on_ext(x)
                
                def on_error(e):
                    if latest == _id:
                        observer.on_error(e)
                
                def on_completed():
                    nonlocal has_latest

                    if latest == _id:
                        has_latest = False;
                        if is_stopped:
                            observer.on_completed()
                        
                d.disposable = inner_source.subscribe(on_next, on_error, on_completed)
            
            def on_completed():
                nonlocal is_stopped

                is_stopped = True
                if not has_latest:
                    observer.on_completed()
                
            subscription = sources.subscribe(on_next, observer.on_error, on_completed)
            return CompositeDisposable(subscription, inner_subscription)
        return AnonymousObservable(subscribe)

    def skip_until(self, other):
        """Returns the values from the source observable sequence only after 
        the other observable sequence produces a value.
     
        other -- The observable sequence that triggers propagation of elements of the source sequence.
     
        Returns an observable sequence containing the elements of the source 
        sequence starting from the point the other sequence triggered 
        propagation.    
        """
    
        source = self

        def subscribe(observer):
            is_open = False

            def on_next(left):
                if is_open:
                    observer.on_next(left)
            
            def on_completed():
                if is_open:
                    observer.on_completed()
            
            disposables = CompositeDisposable(source.subscribe(on_next, observer.on_error, on_completed))

            right_subscription = SingleAssignmentDisposable()
            disposables.add(right_subscription)

            def on_next2(x):
                nonlocal is_open

                is_open = True
                right_subscription.dispose()
            
            def on_completed2():
                right_subscription.dispose()

            right_subscription.disposable = other.subscribe(on_next2, observer.on_error, on_completed2)

            return disposables;
        return AnonymousObservable(subscribe)

    def take_until(self, other):
        """Returns the values from the source observable sequence until the 
        other observable sequence produces a value.

        Keyword arguments:    
        other -- Observable sequence that terminates propagation of elements of 
            the source sequence.
    
        Returns an observable sequence containing the elements of the source 
        sequence up to the point the other sequence interrupted further propagation.
        """
        source = self

        def subscribe(observer):
            def on_completed(x):
                observer.on_completed()

            return CompositeDisposable(
                source.subscribe(observer),
                other.subscribe(on_completed, observer.on_error, noop)
            )
        return AnonymousObservable(subscribe)

