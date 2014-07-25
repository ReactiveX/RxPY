from six import add_metaclass

from rx.internal import Enumerable, Enumerator
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class EnumerableWhileDo(Enumerable):
    """Uses a meta class to extend Enumerable with the methods in this class"""
    
    @classmethod
    def while_do(cls, condition, source):
        def next():
            while condition(source):
                yield source
            
            raise StopIteration()
        return Enumerable(next())

    