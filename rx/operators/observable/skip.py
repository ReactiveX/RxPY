from rx.core import ObservableBase, AnonymousObservable
from rx.internal import ArgumentOutOfRangeException


def skip(count: int, source: ObservableBase) -> ObservableBase:
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

    def subscribe(observer, scheduler=None):
        remaining = count

        def send(value):
            nonlocal remaining

            if remaining <= 0:
                observer.send(value)
            else:
                remaining -= 1

        return observable.subscribe_callbacks(send, observer.throw, observer.close, scheduler)
    return AnonymousObservable(subscribe)
