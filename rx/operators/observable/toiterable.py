from rx.core import Observable, AnonymousObservable


def to_iterable(source: Observable) -> Observable:
    """Creates an iterable from an observable sequence.

    :returns: An observable sequence containing a single element with a list
    containing all the elements of the source sequence.
    :rtype: Observable
    """

    def subscribe(observer):
        nonlocal source

        queue = []

        def on_next(item):
            queue.append(item)

        def on_completed():
            observer.on_next(queue)
            observer.on_completed()

        return source.subscribe_callbacks(on_next, observer.on_error, on_completed)
    return AnonymousObservable(subscribe)
