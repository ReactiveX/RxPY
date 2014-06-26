from six import add_metaclass

from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.internal import SequenceContainsNoElementsError

@add_metaclass(ObservableMeta)
class ObservableLeave(Observable):
    """Note that we do some magic here by using a meta class to extend 
    Observable with the methods in this class"""

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
