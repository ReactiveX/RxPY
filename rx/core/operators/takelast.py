from typing import Callable
from rx.core import Observable, AnonymousObservable


def _take_last(count: int) -> Callable[[Observable], Observable]:
    def take_last(source: Observable) -> Observable:
        """Returns a specified number of contiguous elements from the end of an
        observable sequence.

        Example:
            >>> res = take_last(source)

        This operator accumulates a buffer with a length enough to store
        elements count elements. Upon completion of the source sequence, this
        buffer is drained on the result sequence. This causes the elements to be
        delayed.

        Args:
            source: Number of elements to take from the end of the source
            sequence.

        Returns:
            An observable sequence containing the specified number of elements
            from the end of the source sequence.
        """

        def subscribe(observer, scheduler=None):
            q = []

            def on_next(x):
                q.append(x)
                if len(q) > count:
                    q.pop(0)

            def on_completed():
                while q:
                    observer.on_next(q.pop(0))
                observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return take_last
