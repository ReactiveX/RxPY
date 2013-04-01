from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable

from rx.disposables import Disposable, CompositeDisposable, SingleAssignmentDisposable
from rx.concurrency import ImmediateScheduler

class ObservableMultiple(object):
    def merge_observable(self):
        sources = self

        def subscribe(observer):
            group = CompositeDisposable()
            is_stopped = False
            m = SingleAssignmentDisposable()
            group.add(m)
            
            def on_next(inner_source):
                inner_subscription = SingleAssignmentDisposable()
                group.add(inner_subscription)

                def on_complete():
                    nonlocal group
                    group.remove(inner_subscription)
                    if is_stopped and len(group) == 1:
                        observer.on_completed()
                    
                disposable = inner_source.subscribe(
                    observer.on_next,
                    observer.on_error, 
                        on_complete)
                
                inner_subscription.disposable = disposable
            
            def on_complete():
                nonlocal is_stopped
                is_stopped = True
                if len(group) == 1:
                    observer.on_completed()
            
            m.disposable = sources.subscribe(on_next, observer.on_error, on_complete)
            return group
        
        return AnonymousObservable(subscribe)

Observable.merge_observable = ObservableMultiple.merge_observable