from datetime import datetime
from typing import Union, Callable

from rx import empty, timer, operators as ops
from rx.core import Observable


def _delay_subscription(duetime: Union[datetime, int]) -> Callable[[Observable], Observable]:
    """Time shifts the observable sequence by delaying the subscription.

    1 - res = source.delay_subscription(5000) # 5s

    duetime -- Absolute or relative time to perform the subscription at.

    Returns time-shifted sequence.
    """

    def delay_subscription(source: Observable) -> Observable:
        def mapper(_) -> Observable:
            return empty()

        return source.pipe(ops.delay_with_mapper(timer(duetime), mapper))
    return delay_subscription
