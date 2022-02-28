from typing import Callable, List, Optional, TypeVar

from reactivex import Observable, abc

_T = TypeVar("_T")


def to_iterable_() -> Callable[[Observable[_T]], Observable[List[_T]]]:
    def to_iterable(source: Observable[_T]) -> Observable[List[_T]]:
        """Creates an iterable from an observable sequence.

        Returns:
            An observable sequence containing a single element with an
            iterable containing all the elements of the source
            sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[List[_T]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
            nonlocal source

            queue: List[_T] = []

            def on_next(item: _T):
                queue.append(item)

            def on_completed():
                nonlocal queue
                observer.on_next(queue)
                queue = []
                observer.on_completed()

            return source.subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return to_iterable


__all__ = ["to_iterable_"]
