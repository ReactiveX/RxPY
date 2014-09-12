from six import add_metaclass

from rx.observable import Observable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableToArray(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def to_list(self):
        """Creates a list from an observable sequence.

        Returns an observable sequence containing a single element with a list
        containing all the elements of the source sequence."""

        def accumulator(res, i):
            res.append(i)
            return res[:]

        return self.scan(accumulator, seed=[]).start_with([]).final_value()

    to_array = to_list