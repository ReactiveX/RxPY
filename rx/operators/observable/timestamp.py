from rx.core import Observable
from rx.concurrency import timeout_scheduler
from rx.internal.utils import Timestamp


def timestamp(source: Observable) -> Observable:
    """Records the timestamp for each value in an observable sequence.

    1 - res = source.timestamp() # produces objects with attributes "value" and
        "timestamp", where value is the original value.
    
    Returns an observable sequence with timestamp information on values.
    """

    def factory(scheduler=None):
        scheduler = scheduler or timeout_scheduler

        def selector(value):
            return Timestamp(value=value, timestamp=scheduler.now)

        return source.map(selector)
    return Observable.defer(factory)
