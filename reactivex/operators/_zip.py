from collections.abc import Iterable
from typing import Any, TypeVar

import reactivex
from reactivex import Observable, abc
from reactivex.internal import curry_flip

_T = TypeVar("_T")
_TOther = TypeVar("_TOther")


@curry_flip
def zip_(
    source: Observable[Any],
    *args: Observable[Any],
) -> Observable[tuple[Any, ...]]:
    """Merges the specified observable sequences into one observable
    sequence by creating a tuple whenever all of the
    observable sequences have produced an element at a corresponding
    index.

    Example:
        >>> res = source.pipe(zip(obs1, obs2))
        >>> res = zip(obs1, obs2)(source)

    Args:
        source: Source observable to zip.
        *args: Additional observables to zip with.

    Returns:
        An observable sequence containing the result of combining
        elements of the sources as a tuple.
    """
    return reactivex.zip(source, *args)


@curry_flip
def zip_with_iterable_(
    source: Observable[_T],
    seq: Iterable[_TOther],
) -> Observable[tuple[_T, _TOther]]:
    """Merges the specified observable sequence and list into one
    observable sequence by creating a tuple whenever all of
    the observable sequences have produced an element at a
    corresponding index.

    Example
        >>> res = source.pipe(zip_with_iterable([1, 2, 3]))
        >>> res = zip_with_iterable([1, 2, 3])(source)

    Args:
        source: Source observable to zip.
        seq: Iterable sequence to zip with.

    Returns:
        An observable sequence containing the result of combining
        elements of the sources as a tuple.
    """

    first = source
    second = iter(seq)

    def subscribe(
        observer: abc.ObserverBase[tuple[_T, _TOther]],
        scheduler: abc.SchedulerBase | None = None,
    ):
        index = 0

        def on_next(left: _T) -> None:
            nonlocal index

            try:
                right = next(second)
            except StopIteration:
                observer.on_completed()
            else:
                result = (left, right)
                observer.on_next(result)

        return first.subscribe(
            on_next, observer.on_error, observer.on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["zip_", "zip_with_iterable_"]
