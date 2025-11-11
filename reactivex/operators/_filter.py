from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip
from reactivex.typing import Predicate, PredicateIndexed

_T = TypeVar("_T")


# pylint: disable=redefined-builtin
@curry_flip
def filter_(source: Observable[_T], predicate: Predicate[_T]) -> Observable[_T]:
    """Filters the elements of an observable sequence based on a predicate.

    Example:
        >>> result = source.pipe(filter(lambda x: x > 5))
        >>> result = filter(lambda x: x > 5)(source)

    Args:
        source: Source observable to filter.
        predicate: A function to test each element for a condition.

    Returns:
        A filtered observable sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[_T], scheduler: abc.SchedulerBase | None
    ) -> abc.DisposableBase:
        def on_next(value: _T):
            try:
                should_run = predicate(value)
            except Exception as ex:  # pylint: disable=broad-except
                observer.on_error(ex)
                return

            if should_run:
                observer.on_next(value)

        return source.subscribe(
            on_next, observer.on_error, observer.on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


@curry_flip
def filter_indexed_(
    source: Observable[_T],
    predicate_indexed: PredicateIndexed[_T] | None = None,
) -> Observable[_T]:
    """Filters the elements of an observable sequence based on a predicate
    by incorporating the element's index.

    Example:
        >>> result = source.pipe(filter_indexed(lambda x, i: i % 2 == 0))
        >>> result = filter_indexed(lambda x, i: i % 2 == 0)(source)

    Args:
        source: Source observable to filter.
        predicate_indexed: A function to test each element with its index.

    Returns:
        A filtered observable sequence.
    """

    def subscribe(observer: abc.ObserverBase[_T], scheduler: abc.SchedulerBase | None):
        count = 0

        def on_next(value: _T):
            nonlocal count
            should_run = True

            if predicate_indexed:
                try:
                    should_run = predicate_indexed(value, count)
                except Exception as ex:  # pylint: disable=broad-except
                    observer.on_error(ex)
                    return
                else:
                    count += 1

            if should_run:
                observer.on_next(value)

        return source.subscribe(
            on_next, observer.on_error, observer.on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["filter_", "filter_indexed_"]
