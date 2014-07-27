from six import add_metaclass

from rx.observable import Observable
from rx.anonymousobservable import AnonymousObservable
from rx.internal import SequenceContainsNoElementsError
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableFinalValue(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

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
