from rx.core import Observable, AnonymousObservable


def to_iterable(source: Observable) -> Observable:
    """Creates an iterable from an observable sequence.

    Returns an observable sequence containing a single element with a list
    containing all the elements of the source sequence.
    """

    def subscribe(observer, scheduler=None):
        nonlocal source

        queue = []

        def send(item):
            queue.append(item)

        def close():
            observer.send(queue)
            observer.close()

        return source.subscribe_callbacks(send, observer.throw, close, scheduler)
    return AnonymousObservable(subscribe)
