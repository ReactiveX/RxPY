from typing import Optional

from rx import timer
from rx.core import Observable, abc, typing


def interval_(
    period: typing.RelativeTime, scheduler: Optional[abc.SchedulerBase] = None
) -> Observable[int]:

    return timer(period, period, scheduler)


__all__ = ["interval_"]
