from typing import Any, Callable

import reactivex
from reactivex import Observable


def with_latest_from_(
    *sources: Observable[Any],
) -> Callable[[Observable[Any]], Observable[Any]]:
    """With latest from operator.

    Merges the specified observable sequences into one observable
    sequence by creating a tuple only when the first
    observable sequence produces an element. The observables can be
    passed either as seperate arguments or as a list.

    Examples:
        >>> op = with_latest_from(obs1)
        >>> op = with_latest_from(obs1, obs2, obs3)

    Returns:
        An observable sequence containing the result of combining
    elements of the sources into a tuple.
    """

    def with_latest_from(source: Observable[Any]) -> Observable[Any]:
        return reactivex.with_latest_from(source, *sources)

    return with_latest_from


__all__ = ["with_latest_from_"]
