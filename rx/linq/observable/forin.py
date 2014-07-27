from six import add_metaclass

from rx import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal import ExtensionMethod
from rx.internal import Enumerable

@add_metaclass(ExtensionMethod)
class ObservableForIn(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def for_in(cls, sources, result_selector):
        """Concatenates the observable sequences obtained by running the 
        specified result selector for each element in source.
        
        sources -- {Array} An array of values to turn into an observable 
            sequence.
        result_selector -- {Function} A function to apply to each item in the 
            sources array to turn it into an observable sequence.
        Returns an observable {Observable} sequence from the concatenated 
        observable sequences."""
        
        return Observable.concat(Enumerable.for_each(sources, result_selector))
