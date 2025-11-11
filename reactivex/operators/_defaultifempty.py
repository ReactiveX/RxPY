from typing import TypeVar

from reactivex import Observable, abc
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def default_if_empty_(
    source: Observable[_T],
    default_value: _T | None = None,
) -> Observable[_T | None]:
    """Returns the elements of the specified sequence or the
    specified value in a singleton sequence if the sequence is
    empty.

    Examples:
        >>> obs = source.pipe(default_if_empty())
        >>> obs = default_if_empty()(source)
        >>> obs = source.pipe(default_if_empty(42))

    Args:
        source: Source observable.
        default_value: The value to return if the sequence is empty.

    Returns:
        An observable sequence that contains the specified default
        value if the source is empty otherwise, the elements of the
        source.
    """

    def subscribe(
        observer: abc.ObserverBase[_T | None],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        found = [False]

        def on_next(x: _T):
            found[0] = True
            observer.on_next(x)

        def on_completed():
            if not found[0]:
                observer.on_next(default_value)
            observer.on_completed()

        return source.subscribe(
            on_next, observer.on_error, on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["default_if_empty_"]
