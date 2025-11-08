from collections.abc import Callable
from typing import TypeVar

from reactivex import Observable, abc, compose, typing
from reactivex import operators as ops

_T = TypeVar("_T")


def buffer_with_time_or_count_(
    timespan: typing.RelativeTime,
    count: int,
    scheduler: abc.SchedulerBase | None = None,
) -> Callable[[Observable[_T]], Observable[list[_T]]]:
    return compose(
        ops.window_with_time_or_count(timespan, count, scheduler),
        ops.flat_map(ops.to_iterable()),
    )


__all__ = ["buffer_with_time_or_count_"]
