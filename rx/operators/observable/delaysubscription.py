from datetime import datetime
from typing import Union

from rx.core import Observable, ObservableBase


def delay_subscription(source, duetime: Union[datetime, int]) -> ObservableBase:
    """Time shifts the observable sequence by delaying the subscription.

    1 - res = source.delay_subscription(5000) # 5s

    duetime -- Absolute or relative time to perform the subscription at.

    Returns time-shifted sequence.
    """

    def mapper(_) -> ObservableBase:
        return Observable.empty()

    return source.delay_with_selector(Observable.timer(duetime), mapper)
