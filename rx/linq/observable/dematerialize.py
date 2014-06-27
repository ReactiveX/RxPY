from six import add_metaclass

from rx.observable import Observable, ObservableMeta
from rx.anonymousobservable import AnonymousObservable

@add_metaclass(ObservableMeta)
class ObservableDematerialize(Observable):

    def dematerialize(self):
        """Dematerializes the explicit notification values of an observable 
        sequence as implicit notifications.
        
        Returns an observable sequence exhibiting the behavior corresponding to
        the source sequence's notification values.
        """
        source = self

        def subscribe(observer):
            def on_next(value):
                return value.accept(observer)

            return source.subscribe(on_next, observer.on_error, observer.on_completed)
        return AnonymousObservable(subscribe)
  