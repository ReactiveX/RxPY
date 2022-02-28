from typing import Callable, List, Optional, TypeVar

from reactivex import Observable, abc

_T = TypeVar("_T")


def skip_last_(count: int) -> Callable[[Observable[_T]], Observable[_T]]:
    def skip_last(source: Observable[_T]) -> Observable[_T]:
        """Bypasses a specified number of elements at the end of an
        observable sequence.

        This operator accumulates a queue with a length enough to store
        the first `count` elements. As more elements are received,
        elements are taken from the front of the queue and produced on
        the result sequence. This causes elements to be delayed.

        Args:
            count: Number of elements to bypass at the end of the
            source sequence.

        Returns:
            An observable sequence containing the source sequence
            elements except for the bypassed ones at the end.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
            q: List[_T] = []

            def on_next(value: _T) -> None:
                front = None
                with source.lock:
                    q.append(value)
                    if len(q) > count:
                        front = q.pop(0)

                if front is not None:
                    observer.on_next(front)

            return source.subscribe(
                on_next, observer.on_error, observer.on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return skip_last


__all__ = ["skip_last_"]
