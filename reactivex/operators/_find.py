from collections.abc import Callable
from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def find_value_(
    source: Observable[_T],
    predicate: Callable[[_T, int, Observable[_T]], bool],
    yield_index: bool,
) -> Observable[_T | int | None]:
    """Searches for an element in an observable sequence.

    Examples:
        >>> res = source.pipe(find_value(lambda x, i, s: x > 3, False))
        >>> res = find_value(lambda x, i, s: x > 3, False)(source)

    Args:
        source: The source observable sequence.
        predicate: A function to test each element.
        yield_index: Whether to yield the index or the value.

    Returns:
        An observable sequence containing the found element or index.
    """

    def subscribe(
        observer: abc.ObserverBase[_T | int | None],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        index = 0

        def on_next(x: _T) -> None:
            nonlocal index
            should_run = False
            try:
                should_run = predicate(x, index, source)
            except Exception as ex:  # pylint: disable=broad-except
                observer.on_error(ex)
                return

            if should_run:
                observer.on_next(index if yield_index else x)
                observer.on_completed()
            else:
                index += 1

        def on_completed():
            observer.on_next(-1 if yield_index else None)
            observer.on_completed()

        return source.subscribe(
            on_next, observer.on_error, on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["find_value_"]
