from six import add_metaclass

from rx import Observable, AnonymousObservable
from rx.internal.utils import adapt_call        
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableSelect(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def select(self, selector, this=None):
        """Projects each element of an observable sequence into a new form by
        incorporating the element's index.
        
        1 - source.select(lambda value: value * value)
        2 - source.select(lambda value, index: value * value + index)
        
        Keyword arguments:
        selector -- A transform function to apply to each source element; the
            second parameter of the function represents the index of the source 
            element.
        this -- [Optional] Object to use as self when executing callback.
        
        Returns an observable sequence whose elements are the result of 
        invoking the transform function on each element of source.
        """
        
        selector = adapt_call(selector)        
        parent = this

        def subscribe(observer):
            count = [0]

            def on_next(value):
                result = None
                try:
                    result = selector(value, count[0], parent)
                except Exception as err:
                    observer.on_error(err)
                else:
                    count[0] += 1
                    observer.on_next(result)

            return self.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)
