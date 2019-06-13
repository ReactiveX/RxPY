from typing import Callable, Optional
from rx.core import Observable, typing


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

        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            q = []

            def on_next(x):
                q.append(x)
                if len(q) > count:
                    q.pop(0)

            def on_completed():
                while q:
                    observer.on_next(q.pop(0))
                observer.on_completed()

            return source.subscribe(
                on_next,
                observer.on_error,
                on_completed,
                scheduler=scheduler
            )
        return Observable(subscribe_observer=subscribe_observer)
    return take_last
