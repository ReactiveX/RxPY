from six import add_metaclass

from rx import Observable
from rx.observable import ObservableMeta

@add_metaclass(ObservableMeta)
class ObservableOf(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    @classmethod
    def of(cls, *args, **kwargs):
        """This method creates a new Observable instance with a variable number 
        of arguments, regardless of number or type of the arguments.

        Example:
        res = rx.Observable.of(1,2,3)

        Returns the observable sequence whose elements are pulled from the given 
        arguments""" 
        
        return Observable.from_array(args, scheduler=kwargs.get("scheduler"))
