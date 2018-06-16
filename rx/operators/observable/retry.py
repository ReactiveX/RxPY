from rx.core import Observable, ObservableBase
from rx.internal.iterable import Iterable


def retry(self, retry_count: int = None) -> ObservableBase:
    """Repeats the source observable sequence the specified number of times
    or until it successfully terminates. If the retry count is not
    specified, it retries indefinitely.

    1 - retried = xs.retry()
    2 - retried = xs.retry(42)

    retry_count -- [Optional] Number of times to retry the sequence. If
    not provided, retry the sequence indefinitely.

    Returns an observable sequence producing the elements of the given
    sequence repeatedly until it terminates successfully.
    """

    return Observable.catch_exception(Iterable.repeat(self, retry_count))
