from six import add_metaclass

from rx import Observable
from rx.internal import ExtensionMethod

class AverageValue(object):
    def __init__(self, sum, count):
        self.sum = sum
        self.count = count

@add_metaclass(ExtensionMethod)
class ObservableAverage(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def average(self, key_selector=None, this=None):
        """Computes the average of an observable sequence of values that are in
        the sequence or obtained by invoking a transform function on each 
        element of the input sequence if present.
     
        Example
        res = source.average();
        res = source.average(lambda x: x.value)
     
        key_selector -- A transform function to apply to each element.
        this -- Object to use as self when executing callback.        
        
        Returns an observable sequence containing a single element with the 
        average of the sequence of values."""
        
        if key_selector:
            return self.select(key_selector, this).average()
        
        def accumulator(prev, cur):
            return AverageValue(sum=prev.sum+cur, count=prev.count+1)
                
        def selector(s):
            if s.count == 0:
                raise Exception('The input sequence was empty')
                
            return s.sum / float(s.count)
            
        seed = AverageValue(sum=0, count=0)
        return self.scan(accumulator, seed).final_value().select(selector)
