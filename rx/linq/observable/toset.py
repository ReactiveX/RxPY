from six import add_metaclass

from rx import Observable, AnonymousObservable
from rx.internal import ExtensionMethod

def to_set(source, set_type):
    def subscribe(observer):
        s = set_type()

        def on_completed():
            observer.on_next(s)
            observer.on_completed()

        return source.subscribe(s.add, observer.on_error, on_completed)
    return AnonymousObservable(subscribe)

@add_metaclass(ExtensionMethod)
class ObservableToArray(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def to_set(self):
        """Converts the observable sequence to a set.

        Returns {Observable} An observable sequence with a single value of a set
        containing the values from the observable sequence."""

        return to_set(self, set)
