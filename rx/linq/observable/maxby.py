from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod
from rx.internal.basic import identity, default_sub_comparer
from rx.internal.exceptions import SequenceContainsNoElementsError

from .min import first_only
from .minby import extrema_by

@add_metaclass(ExtensionMethod)
class ObservableMaxBy(Observable):
    def max_by(self, key_selector, comparer):
        """Returns the elements in an observable sequence with the maximum 
        key value according to the specified comparer.
        
        Example
        res = source.max_by(lambda x: x.value)
        res = source.max_by(lambda x: x.value, lambda x, y: x - y)

        Keyword arguments:
        key_selector -- {Function} Key selector function.
        comparer -- {Function} [Optional] Comparer used to compare key values.
        
        Returns an observable {Observable} sequence containing a list of zero 
        or more elements that have a maximum key value."""

        comparer = comparer or default_sub_comparer
        return extrema_by(self, key_selector, comparer)
