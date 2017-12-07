from rx import Observable, AnonymousObservable


def take_last(count: int, source: Observable):
    """Returns a specified number of contiguous elements from the end of an
    observable sequence.

    Example:
    res = source.take_last(5)

    Description:
    This operator accumulates a buffer with a length enough to store
    elements count elements. Upon completion of the source sequence, this
    buffer is drained on the result sequence. This causes the elements to be
    delayed.

    Keyword arguments:
    :param count: Number of elements to take from the end of the source
        sequence.

    :returns: An observable sequence containing the specified number of elements
        from the end of the source sequence.
    :rtype: Observable
    """

    observable = source

    def subscribe(observer, scheduler=None):
        q = []

        def send(x):
            q.append(x)
            if len(q) > count:
                q.pop(0)

        def close():
            while len(q):
                observer.send(q.pop(0))
            observer.close()

        return observable.subscribe_callbacks(send, observer.throw, close, scheduler)
    return AnonymousObservable(subscribe)
