from rx.core import ObservableBase, AnonymousObservable
from rx.internal import extensionmethod


@extensionmethod(ObservableBase)
def dematerialize(self):
    """Dematerializes the explicit notification values of an observable
    sequence as implicit notifications.

    Returns an observable sequence exhibiting the behavior corresponding to
    the source sequence's notification values.
    """

    source = self

    def subscribe(observer, scheduler=None):
        def send(value):
            return value.accept(observer)

        return source.subscribe_callbacks(send, observer.throw, observer.close)
    return AnonymousObservable(subscribe)
