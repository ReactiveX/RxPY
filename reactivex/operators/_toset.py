from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def to_set_(source: Observable[_T]) -> Observable[set[_T]]:
    """Converts the observable sequence to a set.

    Returns an observable sequence with a single value of a set
    containing the values from the observable sequence.

    Examples:
        >>> res = source.pipe(to_set())
        >>> res = to_set()(source)

    Args:
        source: Source observable.

    Returns:
        An observable sequence with a single value of a set
        containing the values from the observable sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[set[_T]],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        s: set[_T] = set()

        def on_completed() -> None:
            nonlocal s
            observer.on_next(s)
            s = set()
            observer.on_completed()

        return source.subscribe(
            s.add, observer.on_error, on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["to_set_"]
