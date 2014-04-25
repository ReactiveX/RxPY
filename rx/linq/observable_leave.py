from rx.concurrency import Scheduler
from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.internal import SequenceContainsNoElementsError

class ObservableLeave(Observable, metaclass=ObservableMeta):

    def final_value(self):
        source = self

        def subscribe(observer):
            has_value = [False]
            value = [None]

            def on_next(x):
                has_value[0] = True
                value[0] = x
            
            def on_completed():
                if not has_value[0]:
                    observer.on_error(SequenceContainsNoElementsError())
                else:
                    observer.on_next(value[0])
                    observer.on_completed()
    
            return source.subscribe(on_next, observer.on_error, on_completed)
        return AnonymousObservable(subscribe)

    def to_array(self):
        def accumulator(res, i):
            res.append(i)
            return res[:]
        
        return self.scan(accumulator, seed=[]).start_with([]).final_value()