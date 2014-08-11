from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableAsObservable(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def as_observable(self):
        """Hides the identity of an observable sequence.

        Returns an observable {Observable} sequence that hides the identity of
        the source sequence."""

        source = self

        def subscribe(observer):
            return source.subscribe(observer)

        return AnonymousObservable(subscribe)

