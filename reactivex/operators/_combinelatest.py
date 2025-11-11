from typing import Any, cast

import reactivex
from reactivex import Observable
from reactivex.internal import curry_flip


@curry_flip
def combine_latest_(
    source: Observable[Any],
    *others: Observable[Any],
) -> Observable[tuple[Any, ...]]:
    """Merges the specified observable sequences into one
    observable sequence by creating a tuple whenever any
    of the observable sequences produces an element.

    Examples:
        >>> result = source.pipe(combine_latest(other1, other2))
        >>> result = combine_latest(other1, other2)(source)

    Args:
        source: The source observable sequence.
        others: Additional observable sequences to combine.

    Returns:
        An observable sequence containing the result of combining
        elements of the sources into a tuple.
    """

    sources: tuple[Observable[Any], ...] = (source, *others)

    ret: Observable[tuple[Any, ...]] = cast(
        Observable[tuple[Any, ...]], reactivex.combine_latest(*sources)
    )
    return ret


__all__ = ["combine_latest_"]
