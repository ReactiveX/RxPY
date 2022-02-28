from typing import Callable, List, Optional, TypeVar

from reactivex import Observable, abc

_T = TypeVar("_T")


def take_last_(count: int) -> Callable[[Observable[_T]], Observable[_T]]:
    def take_last(source: Observable[_T]) -> Observable[_T]:
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

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            q: List[_T] = []

            def on_next(x: _T) -> None:
                q.append(x)
                if len(q) > count:
                    q.pop(0)

            def on_completed():
                while q:
                    observer.on_next(q.pop(0))
                observer.on_completed()

            return source.subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return take_last


__all__ = ["take_last_"]
