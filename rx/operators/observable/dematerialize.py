from rx.core import ObservableBase, AnonymousObservable


def dematerialize(self) -> ObservableBase:
    """Dematerializes the explicit notification values of an observable
    sequence as implicit notifications.

    Returns an observable sequence exhibiting the behavior corresponding to
    the source sequence's notification values.
    """

    source = self

    def subscribe(observer, scheduler=None):
        def send(value):
            return value.accept(observer)

        return source.subscribe_(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)
