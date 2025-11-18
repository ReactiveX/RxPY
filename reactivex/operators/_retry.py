from typing import TypeVar

import reactivex
from reactivex import Observable
from reactivex.internal import curry_flip
from reactivex.internal.utils import infinite

_T = TypeVar("_T")


@curry_flip
def retry_(
    source: Observable[_T],
    retry_count: int | None = None,
) -> Observable[_T]:
    """Repeats the source observable sequence the specified number of
    times or until it successfully terminates. If the retry count is
    not specified, it retries indefinitely.

    Examples:
        >>> result = source.pipe(retry())
        >>> result = retry()(source)
        >>> result = source.pipe(retry(42))

    Args:
        source: The source observable sequence.
        retry_count: Optional number of times to retry the sequence.
            If not provided, retry the sequence indefinitely.

    Returns:
        An observable sequence producing the elements of the given
        sequence repeatedly until it terminates successfully.
    """

    if retry_count is None:
        gen = infinite()
    else:
        gen = range(retry_count)

    return reactivex.catch_with_iterable(source for _ in gen)


__all__ = ["retry_"]
