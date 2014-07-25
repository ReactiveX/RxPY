from six import add_metaclass

from rx import AnonymousObservable, Observable
from rx.internal import ExtensionMethod
from rx.internal.basic import identity
from rx.internal.exceptions import SequenceContainsNoElementsError

def first_only(x):
    if not len(x):
        raise SequenceContainsNoElementsError()
    
    return x[0]

@add_metaclass(ExtensionMethod)
class ObservableMin(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def min(self, comparer=None):
        """Returns the minimum element in an observable sequence according to 
        the optional comparer else a default greater than less than check.
        
        Example
        res = source.min()
        res = source.min(lambda x, y: x.value - y.value)
     
        comparer -- {Function} [Optional] Comparer used to compare elements.
        
        Returns an observable sequence {Observable} containing a single element
        with the minimum element in the source sequence."""

        return self.min_by(identity, comparer).select(lambda x: first_only(x))

