from typing import Callable, List, Optional, TypeVar

from reactivex import Observable, abc, compose
from reactivex import operators as ops
from reactivex import typing

_T = TypeVar("_T")


def buffer_with_time_or_count_(
    timespan: typing.RelativeTime,
    count: int,
    scheduler: Optional[abc.SchedulerBase] = None,
) -> Callable[[Observable[_T]], Observable[List[_T]]]:
    return compose(
        ops.window_with_time_or_count(timespan, count, scheduler),
        ops.flat_map(ops.to_iterable()),
    )


__all__ = ["buffer_with_time_or_count_"]
