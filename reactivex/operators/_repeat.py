from typing import TypeVar

import reactivex
from reactivex import Observable
from reactivex.internal import curry_flip
from reactivex.internal.utils import infinite

_T = TypeVar("_T")


@curry_flip
def repeat_(
    source: Observable[_T],
    repeat_count: int | None = None,
) -> Observable[_T]:
    """Repeats the observable sequence a specified number of times.
    If the repeat count is not specified, the sequence repeats
    indefinitely.

    Examples:
        >>> result = source.pipe(repeat())
        >>> result = repeat()(source)
        >>> result = source.pipe(repeat(42))

    Args:
        source: The observable source to repeat.
        repeat_count: Optional number of times to repeat the sequence.
            If not provided, repeats indefinitely.

    Returns:
        The observable sequence producing the elements of the given
        sequence repeatedly.
    """

    if repeat_count is None:
        gen = infinite()
    else:
        gen = range(repeat_count)

    return reactivex.defer(
        lambda _: reactivex.concat_with_iterable(source for _ in gen)
    )


__all = ["repeat"]
