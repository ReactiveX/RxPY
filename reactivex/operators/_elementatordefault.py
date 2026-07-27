from typing import TypeVar, cast

from reactivex import Observable, abc
from reactivex.internal import curry_flip
from reactivex.internal.exceptions import ArgumentOutOfRangeException

_T = TypeVar("_T")


@curry_flip
def element_at_or_default_(
    source: Observable[_T],
    index: int,
    has_default: bool = False,
    default_value: _T | None = None,
) -> Observable[_T]:
    """Returns the element at a specified index in a sequence or a default value
    if the index is out of range.

    Examples:
        >>> result = source.pipe(element_at_or_default(5))
        >>> result = element_at_or_default(5)(source)
        >>> result = source.pipe(element_at_or_default(5, True, 0))

    Args:
        source: The source observable sequence.
        index: The zero-based index of the element to retrieve.
        has_default: Whether to return a default value if index is out of range.
        default_value: The default value to return if has_default is True.

    Returns:
        An observable sequence that produces the element at the specified
        position in the source sequence, or a default value if the index is
        out of range.

    Raises:
        ArgumentOutOfRangeException: If index is negative.
    """
    if index < 0:
        raise ArgumentOutOfRangeException()

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
    ) -> abc.DisposableBase:
        index_ = index

        def on_next(x: _T) -> None:
            nonlocal index_
            found = False
            with source.lock:
                if index_:
                    index_ -= 1
                else:
                    found = True

            if found:
                observer.on_next(x)
                observer.on_completed()

        def on_completed():
            if not has_default:
                observer.on_error(ArgumentOutOfRangeException())
            else:
                observer.on_next(cast(_T, default_value))
                observer.on_completed()

        return source.subscribe(
            on_next, observer.on_error, on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["element_at_or_default_"]
