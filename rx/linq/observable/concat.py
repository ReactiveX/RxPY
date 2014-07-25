import six
from six import add_metaclass

from rx import AnonymousObservable
from rx.disposables import Disposable, SingleAssignmentDisposable, CompositeDisposable, SerialDisposable
from rx.concurrency import immediate_scheduler
from rx.linq.enumerable import Enumerable
from rx.observable import Observable, ObservableMeta

@add_metaclass(ObservableMeta)
class ObservableConcat(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def __init__(self, subscribe):
        self.concat = self.__concat # Stitch in instance method

    def __concat(self, *args):
        """Concatenates all the observable sequences. This takes in either an 
        array or variable arguments to concatenate.
     
        1 - concatenated = xs.concat(ys, zs)
        2 - concatenated = xs.concat([ys, zs])
     
        Returns an observable sequence that contains the elements of each given
        sequence, in sequential order. 
        """
        
        if isinstance(args[0], list):
            items = args[0]
        else:
            items = list(args)

        items.insert(0, self)
        return Observable.concat(items)
    
    @classmethod
    def concat(cls, *args):
        """Concatenates all the observable sequences.
    
        1 - res = Observable.concat(xs, ys, zs)
        2 - res = Observable.concat([xs, ys, zs])
     
        Returns an observable sequence that contains the elements of each given
        sequence, in sequential order.
        """
        
        if isinstance(args[0], list) or isinstance(args[0], Enumerable):
            sources = args[0]
        else:
            sources = list(args)
            
        def subscribe(observer):
            enum = iter(sources)
            is_disposed = [False]
            subscription = SerialDisposable()

            def action(action1, state=None):
                current = None
                
                if is_disposed[0]:
                    return
                try:
                    current = six.next(enum)
                except StopIteration:
                    observer.on_completed()    
                except Exception as ex:
                    observer.on_error(ex)
                else:
                    d = SingleAssignmentDisposable()
                    subscription.disposable = d
                    d.disposable = current.subscribe(
                        observer.on_next,
                        observer.on_error,
                        lambda: action1()
                    )

            cancelable = immediate_scheduler.schedule_recursive(action)
            
            def dispose():
                is_disposed[0] = True
            return CompositeDisposable(subscription, cancelable, Disposable(dispose))
        return AnonymousObservable(subscribe)

    def concat_all(self):
        """Concatenates an observable sequence of observable sequences.
        
        Returns an observable sequence that contains the elements of each 
        observed inner sequence, in sequential order.
        """
        return self.merge(1)
