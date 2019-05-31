from typing import Optional

from rx import timer
from rx.core import Observable, typing


def _interval(period: typing.RelativeTime,
              scheduler: Optional[typing.Scheduler] = None
              ) -> Observable:

    return timer(period, period, scheduler)
