from typing import TypeVar

from reactivex import Observable, abc, compose, typing
from reactivex import operators as ops
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def buffer_with_time_or_count_(
    source: Observable[_T],
    timespan: typing.RelativeTime,
    count: int,
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[list[_T]]:
    """Buffers elements based on timing and count information.

    Examples:
        >>> source.pipe(buffer_with_time_or_count(1.0, 10))
        >>> buffer_with_time_or_count(1.0, 10)(source)

    Args:
        source: Source observable to buffer.
        timespan: Maximum time length of each buffer.
        count: Maximum element count of each buffer.
        scheduler: Scheduler to use for timing.

    Returns:
        An observable sequence of buffers.
    """
    return source.pipe(
        compose(
            ops.window_with_time_or_count(timespan, count, scheduler),
            ops.flat_map(ops.to_iterable()),
        )
    )


__all__ = ["buffer_with_time_or_count_"]
