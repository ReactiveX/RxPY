from rx import Observable, AnonymousObservable
from rx.internal import ArgumentOutOfRangeException


def skip(count: int, source: Observable):
    """Bypasses a specified number of elements in an observable sequence
    and then returns the remaining elements.

    Keyword arguments:
    count -- The number of elements to skip before returning the remaining
        elements.

    Returns an observable sequence that contains the elements that occur
    after the specified index in the input sequence.
    """

    if count < 0:
        raise ArgumentOutOfRangeException()

    observable = source

    def subscribe(observer):
        remaining = count

        def on_next(value):
            nonlocal remaining

            if remaining <= 0:
                observer.on_next(value)
            else:
                remaining -= 1

        return observable.subscribe(on_next, observer.on_error, observer.on_completed)
    return AnonymousObservable(subscribe)
