from six import add_metaclass

from rx import Observable
from rx.internal import ExtensionMethod

from .firstordefault import first_or_default_async

@add_metaclass(ExtensionMethod)
class ObservableFirst(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def first(self, predicate=None):
        """Returns the first element of an observable sequence that satisfies 
        the condition in the predicate if present else the first item in the 
        sequence.
        
        Example:
        res = res = source.first()
        res = res = source.first(lambda x: x > 3)
        
        Keyword arguments:
        predicate -- {Function} [Optional] A predicate function to evaluate for 
            elements in the source sequence.
        
        Returns {Observable} Sequence containing the first element in the 
        observable sequence that satisfies the condition in the predicate if 
        provided, else the first item in the sequence."""

        return self.where(predicate).first() if predicate else first_or_default_async(self, False)

