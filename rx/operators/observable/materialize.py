from rx.core import ObservableBase, AnonymousObservable
from rx.core.notification import OnNext, OnError, OnCompleted
from rx.internal import extensionmethod


@extensionmethod(ObservableBase)
def materialize(self):
    """Materializes the implicit notifications of an observable sequence as
    explicit notification values.

    Returns an observable sequence containing the materialized notification
    values from the source sequence.
    """

    source = self

    def subscribe(observer, scheduler=None):
        def send(value):
            observer.send(OnNext(value))

        def throw(exception):
            observer.send(OnError(exception))
            observer.close()

        def close():
            observer.send(OnCompleted())
            observer.close()

        return source.subscribe_callbacks(send, throw, close, scheduler)
    return AnonymousObservable(subscribe)

