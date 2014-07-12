from six import add_metaclass

from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable
from rx.notification import OnNext, OnError, OnCompleted

@add_metaclass(ObservableMeta)
class ObservableMaterialize(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def materialize(self):
        """Materializes the implicit notifications of an observable sequence as
        explicit notification values.
        
        Returns an observable sequence containing the materialized notification
        values from the source sequence.
        """
        source = self

        def subscribe(observer):
            def on_next(value):
                observer.on_next(OnNext(value))

            def on_error(exception):
                observer.on_next(OnError(exception))
                observer.on_completed()
            
            def on_completed():
                observer.on_next(OnCompleted())
                observer.on_completed()
            
            return source.subscribe(on_next, on_error, on_completed)
        return AnonymousObservable(subscribe)
    
