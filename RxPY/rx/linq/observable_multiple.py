from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable
from rx.concurrency import ImmediateScheduler

class ObservableMultiple(Observable, metaclass=ObservableMeta):
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
                    on_complete
                )
                inner_subscription.disposable = disposable
            
            def on_complete():
                nonlocal is_stopped
                is_stopped = True
                if group.length == 1:
                    observer.on_completed()
            
            m.disposable = sources.subscribe(on_next, observer.on_error, on_complete)
            return group
        
        return AnonymousObservable(subscribe)
