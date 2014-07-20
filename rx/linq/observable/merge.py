from six import add_metaclass

from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.concurrency import immediate_scheduler

@add_metaclass(ObservableMeta)
class ObservableMerge(Observable):
    def __init__(self, subscribe):
        self.merge = self.__merge

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
            active_count = [0]
            group = CompositeDisposable()
            is_stopped = [False]
            q = []
            
            def subscribe(xs):
                subscription = SingleAssignmentDisposable()
                group.add(subscription)
                
                def on_completed():
                    group.remove(subscription)
                    if q.length > 0:
                        s = q.shift()
                        subscribe(s)
                    else:
                        active_count[0] -= 1
                        if is_stopped[0] and active_count[0] == 0:
                            observer.on_completed()
                        
                subscription.disposable = xs.subscribe(observer.on_next, observer.on_error, on_completed)
            
            def on_next(inner_source):
                if active_count[0] < max_concurrent_or_other:
                    active_count[0] += 1
                    subscribe(inner_source)
                else:
                    q.append(inner_source)

            def on_completed():
                is_stopped[0] = True
                if active_count[0] == 0:
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
                if len(group) == 1:
                    observer.on_completed()

            m.disposable = sources.subscribe(on_next, observer.on_error, on_completed)
            return group

        return AnonymousObservable(subscribe)

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
            is_stopped = [False]
            group.add(m)
            
            def on_next(inner_source):
                inner_subscription = SingleAssignmentDisposable()
                group.add(inner_subscription)

                def on_complete():
                    group.remove(inner_subscription)
                    if is_stopped[0] and group.length == 1:
                        observer.on_completed()
                    
                disposable = inner_source.subscribe(
                    observer.on_next,
                    observer.on_error, 
                    on_complete)
                
                inner_subscription.disposable = disposable
            
            def on_complete():
                is_stopped[0] = True
                if group.length == 1:
                    observer.on_completed()
            
            m.disposable = sources.subscribe(on_next, observer.on_error, on_complete)
            return group
        
        return AnonymousObservable(subscribe)
