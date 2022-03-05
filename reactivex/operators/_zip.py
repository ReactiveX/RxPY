from typing import Any, Callable, Iterable, Optional, Tuple, TypeVar

import reactivex
from reactivex import Observable, abc

_T = TypeVar("_T")
_TOther = TypeVar("_TOther")


def zip_(
    *args: Observable[Any],
) -> Callable[[Observable[Any]], Observable[Tuple[Any, ...]]]:
    def _zip(source: Observable[Any]) -> Observable[Tuple[Any, ...]]:
        """Merges the specified observable sequences into one observable
        sequence by creating a tuple whenever all of the
        observable sequences have produced an element at a corresponding
        index.

        Example:
            >>> res = zip(source)

        Args:
            source: Source observable to zip.

        Returns:
            An observable sequence containing the result of combining
            elements of the sources as a tuple.
        """
        return reactivex.zip(source, *args)

    return _zip


def zip_with_iterable_(
    seq: Iterable[_TOther],
) -> Callable[[Observable[_T]], Observable[Tuple[_T, _TOther]]]:
    def zip_with_iterable(source: Observable[_T]) -> Observable[Tuple[_T, _TOther]]:
        """Merges the specified observable sequence and list into one
        observable sequence by creating a tuple whenever all of
        the observable sequences have produced an element at a
        corresponding index.

        Example
            >>> res = zip(source)

        Args:
            source: Source observable to zip.

        Returns:
            An observable sequence containing the result of combining
            elements of the sources as a tuple.
        """

        first = source
        second = iter(seq)

        def subscribe(
            observer: abc.ObserverBase[Tuple[_T, _TOther]],
            scheduler: Optional[abc.SchedulerBase] = None,
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

    return zip_with_iterable


__all__ = ["zip_", "zip_with_iterable_"]
