from typing import Callable
from rx.core import Observable


def _take_last_buffer(count: int) -> Callable[[Observable], Observable]:
    def take_last_buffer(source: Observable) -> Observable:
        """Returns an array with the specified number of contiguous
        elements from the end of an observable sequence.

        Example:
            >>> res = take_last(source)

        This operator accumulates a buffer with a length enough to
        store elements count elements. Upon completion of the source
        sequence, this buffer is drained on the result sequence. This
        causes the elements to be delayed.

        Args:
            source: Source observable to take elements from.

        Returns:
            An observable sequence containing a single list with the
            specified number of elements from the end of the source
            sequence.
        """

        def subscribe(observer, scheduler=None):
            q = []

            def on_next(x):
                with source.lock:
                    q.append(x)
                    if len(q) > count:
                        q.pop(0)

            def on_completed():
                observer.on_next(q)
                observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
        return Observable(subscribe)
    return take_last_buffer
