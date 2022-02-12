from typing import Callable, List, Optional, TypeVar

from rx import operators as ops
from rx.core import Observable, abc, pipe, typing

_T = TypeVar("_T")


def buffer_with_time_(
    timespan: typing.RelativeTime,
    timeshift: Optional[typing.RelativeTime] = None,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    if not timeshift:
        timeshift = timespan

    return pipe(
        ops.window_with_time(timespan, timeshift, scheduler),
        ops.flat_map(ops.to_list()),
    )


__all__ = ["buffer_with_time_"]
