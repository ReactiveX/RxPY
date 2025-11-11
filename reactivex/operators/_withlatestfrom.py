from typing import Any

import reactivex
from reactivex import Observable
from reactivex.internal import curry_flip


@curry_flip
def with_latest_from_(
    source: Observable[Any],
    *sources: Observable[Any],
) -> Observable[Any]:
    """With latest from operator.

    Merges the specified observable sequences into one observable
    sequence by creating a tuple only when the first
    observable sequence produces an element. The observables can be
    passed either as seperate arguments or as a list.

    Examples:
        >>> res = source.pipe(with_latest_from(obs1))
        >>> res = source.pipe(with_latest_from(obs1, obs2, obs3))
        >>> res = with_latest_from(obs1)(source)

    Args:
        source: Source observable.
        *sources: Additional observables to combine with.

    Returns:
        An observable sequence containing the result of combining
    elements of the sources into a tuple.
    """
    return reactivex.with_latest_from(source, *sources)


__all__ = ["with_latest_from_"]
