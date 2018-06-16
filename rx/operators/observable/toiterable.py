from rx.core import ObservableBase, AnonymousObservable


def to_iterable(source: ObservableBase) -> ObservableBase:
    """Creates an iterable from an observable sequence.

    Returns an observable sequence containing a single element with a list
    containing all the elements of the source sequence.
    """

    def subscribe(observer, scheduler=None):
        nonlocal source

        queue = []

        def on_next(item):
            queue.append(item)

        def on_completed():
            observer.on_next(queue)
            observer.on_completed()

        return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
    return AnonymousObservable(subscribe)
