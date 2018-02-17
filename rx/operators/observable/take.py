from rx.core import ObservableBase, Observable, AnonymousObservable
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

        def on_next(value):
            nonlocal remaining

            if remaining > 0:
                remaining -= 1
                observer.on_next(value)
                if not remaining:
                    observer.on_completed()

        return observable.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
    return AnonymousObservable(subscribe)
