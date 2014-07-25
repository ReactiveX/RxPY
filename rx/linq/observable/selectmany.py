from six import add_metaclass

from rx import Observable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableSelectMany(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def select_many(self, selector, result_selector=None):
        """One of the Following:
        Projects each element of an observable sequence to an observable 
        sequence and merges the resulting observable sequences into one 
        observable sequence.
        
        1 - source.select_many(lambda x: Observable.range(0, x))
        
        Or:
        Projects each element of an observable sequence to an observable 
        sequence, invokes the result selector for the source element and each 
        of the corresponding inner sequence's elements, and merges the results
        into one observable sequence.
        
        1 - source.select_many(lambda x: Observable.range(0, x), lambda x, y: x + y)
        
        Or:
        Projects each element of the source observable sequence to the other
        observable sequence and merges the resulting observable sequences into
        one observable sequence.
        
        1 - source.select_many(Observable.from_array([1,2,3]))
        
        Keyword arguments:
        selector -- A transform function to apply to each element or an 
            observable sequence to project each element from the source 
            sequence onto.
        result_selector -- [Optional] A transform function to apply to each
            element of the intermediate sequence.
        
        Returns an observable sequence whose elements are the result of 
        invoking the one-to-many transform function collectionSelector on each
        element of the input sequence and then mapping each of those sequence 
        elements and their corresponding source element to a result element.        
        """
        def select_many(selector):
            return self.select(selector).merge_observable()
        
        if result_selector:
            def projection(x):
                return selector(x).select(lambda y, i: result_selector(x, y))
            return self.select_many(projection)
                
        if not isinstance(selector, Observable):
            return select_many(selector)
        
        def get_selector(value, i=None):
            return selector
        return select_many(get_selector)
