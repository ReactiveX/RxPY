from collections.abc import Callable
from typing import TypeVar

from reactivex import Observable, abc, compose, typing
from reactivex import operators as ops

_T = TypeVar("_T")


def buffer_with_time_(
    timespan: typing.RelativeTime,
    timeshift: typing.RelativeTime | None = None,
    scheduler: abc.SchedulerBase | None = None,
) -> Callable[[Observable[_T]], Observable[list[_T]]]:
    if not timeshift:
        timeshift = timespan

    return compose(
        ops.window_with_time(timespan, timeshift, scheduler),
        ops.flat_map(ops.to_list()),
    )


__all__ = ["buffer_with_time_"]
