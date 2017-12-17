from rx.core import ObservableBase, AnonymousObservable
from rx.internal import ArgumentOutOfRangeException


def take(count: int, source: ObservableBase):
    """Returns a specified number of contiguous elements from the start of
    an observable sequence.

    1 - source.take(5)

    Keyword arguments:
    count -- The number of elements to return.

    Returns an observable sequence that contains the specified number of
    elements from the start of the input sequence.
    """

    if count < 0:
        raise ArgumentOutOfRangeException()

    if not count:
        return Observable.empty()

    observable = source

    def subscribe(observer, scheduler=None):
        remaining = count

        def send(value):
            nonlocal remaining

            if remaining > 0:
                remaining -= 1
                observer.send(value)
                if not remaining:
                    observer.close()

        return observable.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)
