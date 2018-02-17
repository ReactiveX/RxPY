from rx.core import ObservableBase, AnonymousObservable


def dematerialize(self) -> ObservableBase:
    """Dematerializes the explicit notification values of an observable
    sequence as implicit notifications.

    Returns an observable sequence exhibiting the behavior corresponding to
    the source sequence's notification values.
    """

    source = self

    def subscribe(observer, scheduler=None):
        def on_next(value):
            return value.accept(observer)

        return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
    return AnonymousObservable(subscribe)
