from typing import Any, TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip
from reactivex.typing import Predicate, PredicateIndexed

_T = TypeVar("_T")


@curry_flip
def take_while_(
    source: Observable[_T],
    predicate: Predicate[_T],
    inclusive: bool = False,
) -> Observable[_T]:
    """Returns elements from an observable sequence as long as a
    specified condition is true.

    Examples:
        >>> result = source.pipe(take_while(lambda x: x < 10))
        >>> result = take_while(lambda x: x < 10)(source)
        >>> result = source.pipe(take_while(lambda x: x < 10, inclusive=True))

    Args:
        source: The source observable to take from.
        predicate: A function to test each element for a condition.
        inclusive: Include the element that fails the predicate.

    Returns:
        An observable sequence that contains the elements from the
        input sequence that occur before the element at which the
        test no longer passes.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        running = True

        def on_next(value: _T):
            nonlocal running

            with source.lock:
                if not running:
                    return

                try:
                    running = predicate(value)
                except Exception as exn:
                    observer.on_error(exn)
                    return

            if running:
                observer.on_next(value)
            else:
                if inclusive:
                    observer.on_next(value)
                observer.on_completed()

        return source.subscribe(
            on_next, observer.on_error, observer.on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


@curry_flip
def take_while_indexed_(
    source: Observable[_T],
    predicate: PredicateIndexed[_T],
    inclusive: bool = False,
) -> Observable[_T]:
    """Returns elements from an observable sequence as long as a
    specified condition is true. The element's index is used in the
    logic of the predicate function.

    Examples:
        >>> result = source.pipe(take_while_indexed(lambda x, i: i < 10))
        >>> result = take_while_indexed(lambda x, i: i < 10)(source)

    Args:
        source: Source observable to take from.
        predicate: A function to test each element with its index.
        inclusive: Include the element that fails the predicate.

    Returns:
        An observable sequence that contains the elements from the
        input sequence that occur before the element at which the
        test no longer passes.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        running = True
        i = 0

        def on_next(value: Any) -> None:
            nonlocal running, i

            with source.lock:
                if not running:
                    return

                try:
                    running = predicate(value, i)
                except Exception as exn:
                    observer.on_error(exn)
                    return
                else:
                    i += 1

            if running:
                observer.on_next(value)
            else:
                if inclusive:
                    observer.on_next(value)
                observer.on_completed()

        return source.subscribe(
            on_next, observer.on_error, observer.on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["take_while_", "take_while_indexed_"]
