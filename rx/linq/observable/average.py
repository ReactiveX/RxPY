from rx import AnonymousObservable, Observable
from rx.observable import ObservableMeta

class ObservableAverage(Observable, metaclass=ObservableMeta):
    def average(self, key_selector=None, self_arg=None):
        """Computes the average of an observable sequence of values that are in
        the sequence or obtained by invoking a transform function on each 
        element of the input sequence if present.
     
        Example
        res = source.average();
        res = source.average(lambda x: x.value)
     
        key_selector -- A transform function to apply to each element.
        self_arg Object to use as self when executing callback.        
        
        Returns an observable sequence containing a single element with the 
        average of the sequence of values."""
        
        if key_selector:
            return self.select(key_selector, self_rg).average()
        else:
            def func(prev, cur):
                return {
                    "sum": prev.sum + cur,
                    "count": prev.count + 1
                }
            def selector(s):
                if s.count == 0:
                    raise Exception('The input sequence was empty')
                
                return s.sum / s.count
            
            return self.scan({
                    "sum": 0,
                    "count": 0
                }, func).final_value().select(selector)
