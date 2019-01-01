from typing import Callable
from rx.core import Observable, StaticObservable
from rx.concurrency import timeout_scheduler
from rx.internal.utils import Timestamp

from .map import map


def timestamp() -> Callable[[Observable], Observable]:
    """Records the timestamp for each value in an observable sequence.

    1 - res = source.timestamp() # produces objects with attributes "value" and
        "timestamp", where value is the original value.

    Returns an observable sequence with timestamp information on values.
    """

    def partial(source: Observable) -> Observable:
        def factory(scheduler=None):
            scheduler = scheduler or timeout_scheduler
            mapper = map(lambda value: Timestamp(value=value, timestamp=scheduler.now))

            return source.pipe(mapper)
        return StaticObservable.defer(factory)
    return partial
