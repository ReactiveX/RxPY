
from rx.internal import Enumerable, noop
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable

from .observable_single import concat

class ObservableMultiple(Observable, metaclass=ObservableMeta):
    def __init__(self, subscribe):
        self.concat = self.__concat # Stitch in instance method
        self.merge = self.__merge

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

    def __merge(self, max_concurrent_or_other):
        """Merges an observable sequence of observable sequences into an 
        observable sequence, limiting the number of concurrent subscriptions
        to inner sequences. Or merges two observable sequences into a single 
        observable sequence.
         
        1 - merged = sources.merge(1)
        2 - merged = source.merge(otherSource)  
         
        max_concurrent_or_other [Optional] Maximum number of inner observable 
            sequences being subscribed to concurrently or the second 
            observable sequence.
        
        Returns the observable sequence that merges the elements of the inner 
        sequences. 
        """
        if isinstance(max_concurrent_or_other, int):
            return Observable.merge(max_concurrent_or_other)
        
        sources = self

        def subscribe(observer):
            active_count = 0
            group = CompositeDisposable()
            is_stopped = False
            q = []
            
            def subscribe(xs):
                subscription = SingleAssignmentDisposable()
                group.add(subscription)
                
                def on_completed():
                    nonlocal active_count
                    
                    group.remove(subscription)
                    if q.length > 0:
                        s = q.shift()
                        subscribe(s)
                    else:
                        active_count -= 1
                        if is_stopped and active_count == 0:
                            observer.on_completed()
                        
                subscription.disposable = xs.subscribe(observer.on_next, observer.on_error, on_completed)
            
            def on_next(inner_source):
                nonlocal active_count

                if active_count < max_concurrent_or_other:
                    active_count += 1
                    subscribe(inner_source)
                else:
                    q.push(inner_source)

            def on_completed():
                nonlocal is_stopped

                is_stopped = True
                if active_count == 0:
                    observer.on_completed()
            
            group.add(sources.subscribe(on_next, observer.on_error, on_completed))
            return group
        return AnonymousObservable(subscribe)

    @classmethod
    def merge(cls, *args):
        """Merges all the observable sequences into a single observable 
        sequence. The scheduler is optional and if not specified, the 
        immediate scheduler is used.
     
        1 - merged = rx.Observable.merge(xs, ys, zs)
        2 - merged = rx.Observable.merge([xs, ys, zs])
        3 - merged = rx.Observable.merge(scheduler, xs, ys, zs)
        4 - merged = rx.Observable.merge(scheduler, [xs, ys, zs])    
     
        Returns the observable sequence that merges the elements of the observable sequences. 
        """
    
        if not args[0]:
            scheduler = immediate_scheduler
            sources = args[1:]
        elif args[0].now:
            scheduler = args[0]
            sources = args[1:]
        else:
            scheduler = immediate_scheduler
            sources = args[0]
        
        if isinstance(sources[0], list):
            sources = sources[0]
        
        return Observable.from_array(sources, scheduler).merge_observable()

    def merge_all(self):
        """Merges an observable sequence of observable sequences into an 
        observable sequence.
        
        Returns the observable sequence that merges the elements of the inner 
        sequences.   
        """
        sources = self

        def subscribe(observer):
            group = CompositeDisposable()
            is_stopped = False
            m = SingleAssignmentDisposable()
            group.add(m)
            
            def on_next(inner_source):
                inner_subscription = SingleAssignmentDisposable()
                group.add(inner_subscription)

                def on_next(x):
                    observer.on_next(x)
                
                def on_completed():
                    group.remove(inner_subscription)
                    if is_stopped and group.length == 1:
                        observer.on_completed()
                    
                inner_subscription.disposable = inner_source.subscribe(on_next, observer.on_error, on_completed)
            
            def on_completed():
                is_stopped = True
                if (group.length == 1):
                    observer.on_completed()

            m.disposable = sources.subscribe(on_next, observer.on_error, on_completed)
            return group

        return AnonymousObservable(subscribe)