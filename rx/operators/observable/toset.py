from rx.core import ObservableBase, AnonymousObservable


def to_set(source: ObservableBase) -> ObservableBase:
    """Converts the observable sequence to a set.

    Returns an observable sequence with a single value of a set
    containing the values from the observable sequence.
    """

    def subscribe(observer, scheduler=None):
        s = set()

        def on_completed():
            observer.on_next(s)
            observer.on_completed()

        return source.subscribe_(s.add, observer.on_error, on_completed, scheduler)
    return AnonymousObservable(subscribe)
