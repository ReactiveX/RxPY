from typing import Callable, Optional

import rx
from rx.core import Observable
from rx.internal.utils import infinite


def _retry(retry_count: Optional[int] = None) -> Callable[[Observable], Observable]:
    """Repeats the source observable sequence the specified number of
    times or until it successfully terminates. If the retry count is
    not specified, it retries indefinitely.

    Examples:
        >>> retried = retry()
        >>> retried = retry(42)

    Args:
        retry_count: [Optional] Number of times to retry the sequence.
            If not provided, retry the sequence indefinitely.

    Returns:
        An observable sequence producing the elements of the given
        sequence repeatedly until it terminates successfully.
    """

    if retry_count is None:
        gen = infinite()
    else:
        gen = range(retry_count)

    def retry(source: Observable) -> Observable:
        return rx.catch_with_iterable(source for _ in gen)
    return retry
