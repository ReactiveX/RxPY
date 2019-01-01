from typing import Callable
from rx.core import Observable, AnonymousObservable


def take_last_buffer(self, count) -> Callable[[Observable], Observable]:
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
    count -- Number of elements to take from the end of the source
        sequence.

    Returns: An observable sequence containing a single list with the specified
    number of elements from the end of the source sequence.
    """

    def partial(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            q = []

            def on_next(x):
                with self.lock:
                    q.append(x)
                    if len(q) > count:
                        q.pop(0)

            def on_completed():
                observer.on_next(q)
                observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return partial
