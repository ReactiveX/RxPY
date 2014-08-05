from six import add_metaclass

from rx import Observable, AnonymousObservable
from rx.internal import ExtensionMethod

from .lastordefault import last_or_default_async

@add_metaclass(ExtensionMethod)
class ObservableLast(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def last(self, predicate=None):
        """Returns the last element of an observable sequence that satisfies the
        condition in the predicate if specified, else the last element.

        Example:
        res = source.last()
        res = source.last(lambda x: x > 3)

        Keyword arguments:
        predicate -- {Function} [Optional] A predicate function to evaluate for
            elements in the source sequence.

        Returns {Observable} Sequence containing the last element in the
        observable sequence that satisfies the condition in the predicate."""

        return self.where(predicate).last() if predicate else last_or_default_async(self, False)
