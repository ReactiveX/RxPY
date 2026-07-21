from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def as_observable_(source: Observable[_T]) -> Observable[_T]:
    """Hides the identity of an observable sequence.

    Examples:
        >>> res = source.pipe(as_observable())
        >>> res = as_observable()(source)

    Args:
        source: Observable source to hide identity from.

    Returns:
        An observable sequence that hides the identity of the
        source sequence.
    """

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        return source.subscribe(observer, scheduler=scheduler)

    return Observable(subscribe)


__all__ = ["as_observable_"]
