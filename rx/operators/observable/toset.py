from rx.core import ObservableBase, AnonymousObservable


def to_set(source: ObservableBase) -> ObservableBase:
    """Converts the observable sequence to a set.

    Returns an observable sequence with a single value of a set
    containing the values from the observable sequence.
    """

    def subscribe(observer, scheduler=None):
        s = set()

        def close():
            observer.send(s)
            observer.close()

        return source.subscribe_callbacks(s.add, observer.throw, close, scheduler)
    return AnonymousObservable(subscribe)
