from rx.concurrency import Scheduler
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.internal import SequenceContainsNoElementsError

class ObservableFinalValue(Observable, metaclass=ObservableMeta):
    def final_value(self):
        source = self

        def subscribe(observer):
            has_value = False
            value = None

            def on_next(x):
                nonlocal has_value, value
                has_value = True
                value = x
            
            def on_completed():
                if not has_value:
                    observer.on_error(SequenceContainsNoElementsError())
                else:
                    observer.on_next(value)
                    observer.on_completed()
    
            return source.subscribe(on_next, observer.on_error, on_completed)
        return AnonymousObservable(subscribe)
