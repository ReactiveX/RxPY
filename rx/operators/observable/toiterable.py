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

        def send(item):
            queue.append(item)

        def close():
            observer.send(queue)
            observer.close()

        return source.subscribe_callbacks(send, observer.throw, close)
    return AnonymousObservable(subscribe)
