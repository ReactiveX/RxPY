from six import add_metaclass

from rx import Observable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservablePluck(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def pluck(self, property):
        """Retrieves the value of a specified property from all elements in the
        Observable sequence.

        Keyword arguments:
        property {String} The property to pluck.

        Returns a new Observable {Observable} sequence of property values."""

        return self.select(lambda x: x[property])
