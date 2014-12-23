from rx import Observable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def pluck(self, property):
    """Retrieves the value of a specified property from all elements in the
    Observable sequence.

    Keyword arguments:
    property {String} The property to pluck.

    Returns a new Observable {Observable} sequence of property values.
    """

    return self.map(lambda x: x[property])
