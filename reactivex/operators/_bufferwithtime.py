from typing import TypeVar

from reactivex import Observable, abc, compose, typing
from reactivex import operators as ops
from reactivex.internal import curry_flip

_T = TypeVar("_T")


@curry_flip
def buffer_with_time_(
    source: Observable[_T],
    timespan: typing.RelativeTime,
    timeshift: typing.RelativeTime | None = None,
    scheduler: abc.SchedulerBase | None = None,
) -> Observable[list[_T]]:
    """Buffers elements based on timing information.

    Examples:
        >>> source.pipe(buffer_with_time(1.0))
        >>> source.pipe(buffer_with_time(1.0, 0.5))
        >>> buffer_with_time(1.0)(source)

    Args:
        source: Source observable to buffer.
        timespan: Length of each buffer.
        timeshift: Interval between creation of consecutive buffers.
        scheduler: Scheduler to use for timing.

    Returns:
        An observable sequence of buffers.
    """
    if not timeshift:
        timeshift = timespan

    return source.pipe(
        compose(
            ops.window_with_time(timespan, timeshift, scheduler),
            ops.flat_map(ops.to_list()),
        )
    )


__all__ = ["buffer_with_time_"]
