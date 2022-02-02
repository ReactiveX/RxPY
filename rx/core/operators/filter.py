from typing import Callable, Optional, TypeVar

from rx.core import Observable, abc
from rx.core.typing import Predicate, PredicateIndexed

_T = TypeVar("_T")

# pylint: disable=redefined-builtin
def _filter(predicate: Predicate[_T]) -> Callable[[Observable[_T]], Observable[_T]]:
    def filter(source: Observable[_T]) -> Observable[_T]:
        """Partially applied filter operator.

        Filters the elements of an observable sequence based on a
        predicate.

        Example:
            >>> filter(source)

        Args:
            source: Source observable to filter.

        Returns:
            A filtered observable sequence.
        """

        def subscribe(observer: abc.ObserverBase[_T], scheduler: Optional[abc.SchedulerBase]) -> abc.DisposableBase:
            def on_next(value: _T):
                try:
                    should_run = predicate(value)
                except Exception as ex:  # pylint: disable=broad-except
                    observer.on_error(ex)
                    return

                if should_run:
                    observer.on_next(value)

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)

        return Observable(subscribe)

    return filter


def _filter_indexed(
    predicate_indexed: Optional[PredicateIndexed[_T]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    def filter_indexed(source: Observable[_T]) -> Observable[_T]:
        """Partially applied indexed filter operator.

        Filters the elements of an observable sequence based on a
        predicate by incorporating the element's index.

        Example:
            >>> filter_indexed(source)

        Args:
            source: Source observable to filter.

        Returns:
            A filtered observable sequence.
        """

        def subscribe(observer: abc.ObserverBase[_T], scheduler: Optional[abc.SchedulerBase]):
            count = 0

            def on_next(value: _T):
                nonlocal count
                try:
                    should_run = predicate_indexed(value, count)
                except Exception as ex:  # pylint: disable=broad-except
                    observer.on_error(ex)
                    return
                else:
                    count += 1

                if should_run:
                    observer.on_next(value)

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)

        return Observable(subscribe)

    return filter_indexed


__all__ = ["_filter", "_filter_indexed"]
