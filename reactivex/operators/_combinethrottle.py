from typing import Any, Callable, Tuple

import reactivex
from reactivex import Observable


def combine_throttle_(
    *args: Observable[Any],
) -> Callable[[Observable[Any]], Observable[Tuple[Any, ...]]]:
    def _combine_throttle(source: Observable[Any]) -> Observable[Tuple[Any, ...]]:
        """Merges the specified observable sequences into one observable
        sequence by creating a tuple whenever all of the observable sequences
        have produced an element at a corresponding index.

        Example:
            >>> res = combine_throttle(source)

        Args:
            args: Observable sources to combine_throttle.

        Returns:
            An observable sequence containing the result of combining
            elements of the sources as a tuple.
        """

        return reactivex.combine_throttle(source, *args)

    return _combine_throttle


__all__ = ["combine_throttle_"]
