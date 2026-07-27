from typing import TypeVar

import reactivex
from reactivex import Observable, abc
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

    The retry budget is per-subscription, so combining ``retry(n)`` with
    ``repeat()`` works as expected: each resubscription by ``repeat()``
    starts with a fresh retry allowance.

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

    def subscribe(
        observer: abc.ObserverBase[_T], scheduler_: abc.SchedulerBase | None = None
    ) -> abc.DisposableBase:
        # Create a fresh generator on every subscription so that the retry
        # budget is not shared across resubscriptions (e.g. via repeat()).
        if retry_count is None:
            gen = infinite()
        else:
            gen = range(retry_count)

        return reactivex.catch_with_iterable(source for _ in gen).subscribe(
            observer, scheduler=scheduler_
        )

    return Observable(subscribe)


__all__ = ["retry_"]
