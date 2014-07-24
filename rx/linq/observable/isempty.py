from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.observable import ObservableMeta

@add_metaclass(ObservableMeta)
class ObservableAll(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def is_empty(self):
        """Determines whether an observable sequence is empty.
        
        Returns an observable {Observable} sequence containing a single element
        determining whether the source sequence is empty."""

        return self.any().select(lambda b: not b)

