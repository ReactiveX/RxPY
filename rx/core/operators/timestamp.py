from typing import Callable

from rx import defer
from rx.core import Observable
from rx.concurrency import timeout_scheduler
from rx.internal.utils import Timestamp
from rx import operators


def timestamp() -> Callable[[Observable], Observable]:
    """Records the timestamp for each value in an observable sequence.

    Examples:
        >>> timestamp()

    Produces objects with attributes `value` and `timestamp`, where
    value is the original value.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence with timestamp information on values.
    """

    def partial(source: Observable) -> Observable:
        def factory(scheduler=None):
            scheduler = scheduler or timeout_scheduler
            mapper = operators.map(lambda value: Timestamp(value=value, timestamp=scheduler.now))

            return source.pipe(mapper)
        return defer(factory)
    return partial
