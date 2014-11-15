from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableAll(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def all(self, predicate):
        """Determines whether all elements of an observable sequence satisfy a
        condition.

        1 - res = source.all(lambda value: value.length > 3)

        predicate -- A function to test each element for a condition.

        Returns an observable sequence containing a single element determining
        whether all elements in the source sequence pass the test in the
        specified predicate."""

        return self.filter(lambda v: not predicate(v)).some().select(lambda b: not b)

    # Alias for all
    every = all
