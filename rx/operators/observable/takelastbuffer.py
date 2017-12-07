from rx import Observable, AnonymousObservable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def take_last_buffer(self, count):
    """Returns an array with the specified number of contiguous elements
    from the end of an observable sequence.

    Example:
    res = source.take_last(5)

    Description:
    This operator accumulates a buffer with a length enough to store
    elements count elements. Upon completion of the source sequence, this
    buffer is drained on the result sequence. This causes the elements to be
    delayed.

    Keyword arguments:
    :param int count: Number of elements to take from the end of the source
        sequence.

    :returns: An observable sequence containing a single list with the specified
    number of elements from the end of the source sequence.
    :rtype: Observable
    """

    source = self

    def subscribe(observer, scheduler=None):
        q = []
        def send(x):
            with self.lock:
                q.append(x)
                if len(q) > count:
                    q.pop(0)

        def close():
            observer.send(q)
            observer.close()

        return source.subscribe_callbacks(send, observer.throw, close, scheduler)
    return AnonymousObservable(subscribe)
