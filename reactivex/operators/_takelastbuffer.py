from typing import Callable, List, Optional, TypeVar

from reactivex import Observable, abc

_T = TypeVar("_T")


def take_last_buffer_(count: int) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    def take_last_buffer(source: Observable[_T]) -> Observable[List[_T]]:
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

        def subscribe(
            observer: abc.ObserverBase[List[_T]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            q: List[_T] = []

            def on_next(x: _T) -> None:
                with source.lock:
                    q.append(x)
                    if len(q) > count:
                        q.pop(0)

            def on_completed() -> None:
                observer.on_next(q)
                observer.on_completed()

            return source.subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return take_last_buffer


__all__ = ["take_last_buffer_"]
