from typing import Any, cast

import reactivex
from reactivex import Observable
from reactivex.internal import curry_flip


@curry_flip
def fork_join_(
    source: Observable[Any],
    *args: Observable[Any],
) -> Observable[tuple[Any, ...]]:
    """Wait for observables to complete and then combine last values
    they emitted into a tuple. Whenever any of that observables
    completes without emitting any value, result sequence will
    complete at that moment as well.

    Examples:
        >>> source.pipe(fork_join(obs1, obs2))
        >>> fork_join(obs1, obs2)(source)

    Args:
        source: Source observable.
        *args: Additional observables to fork_join with.

    Returns:
        An observable sequence containing the result of combining
        last element from each source in given sequence.
    """
    return cast(Observable[tuple[Any, ...]], reactivex.fork_join(source, *args))


__all__ = ["fork_join_"]
