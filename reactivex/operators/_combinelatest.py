from typing import Any, Callable

import reactivex
from reactivex import Observable


def combine_latest_(
    *others: Observable[Any],
) -> Callable[[Observable[Any]], Observable[Any]]:
    def combine_latest(source: Observable[Any]) -> Observable[Any]:
        """Merges the specified observable sequences into one
        observable sequence by creating a tuple whenever any
        of the observable sequences produces an element.

        Examples:
            >>> obs = combine_latest(source)

        Returns:
            An observable sequence containing the result of combining
            elements of the sources into a tuple.
        """

        sources = (source,) + others

        return reactivex.combine_latest(*sources)

    return combine_latest


__all__ = ["combine_latest_"]
