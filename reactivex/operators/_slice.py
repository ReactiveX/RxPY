from sys import maxsize
from typing import Any, TypeVar

from reactivex import Observable, abc, defer
from reactivex import operators as ops
from reactivex.internal import curry_flip

_T = TypeVar("_T")


# pylint: disable=redefined-builtin
@curry_flip
def slice_(
    source: Observable[_T],
    start: int | None = None,
    stop: int | None = None,
    step: int | None = None,
) -> Observable[_T]:
    """Slices the given observable.

    It is basically a wrapper around the operators
    :func:`skip <reactivex.operators.skip>`,
    :func:`skip_last <reactivex.operators.skip_last>`,
    :func:`take <reactivex.operators.take>`,
    :func:`take_last <reactivex.operators.take_last>` and
    :func:`filter <reactivex.operators.filter>`.

    The following diagram helps you remember how slices works with streams.

    Positive numbers are relative to the start of the events, while negative
    numbers are relative to the end (close) of the stream.

    .. code::

        r---e---a---c---t---i---v---e---!
        0   1   2   3   4   5   6   7   8
       -8  -7  -6  -5  -4  -3  -2  -1   0

    Examples:
        >>> result = source.pipe(slice(1, 10))
        >>> result = slice(1, 10)(source)
        >>> result = source.pipe(slice(1, -2))
        >>> result = source.pipe(slice(1, -1, 2))

    Args:
        source: Observable to slice
        start: Start index
        stop: Stop index
        step: Step size

    Returns:
        A sliced observable sequence.
    """
    _start: int = 0 if start is None else start
    _stop: int = maxsize if stop is None else stop
    _step: int = 1 if step is None else step

    if _step < 0:
        # Reversing events is not supported
        raise TypeError("Negative step not supported.")

    if _start < 0 and stop is not None and _stop > 0:
        return _slice_mixed_bounds(source, _start, _stop, _step)

    pipeline: list[Any] = []

    if _stop >= 0:
        pipeline.append(ops.take(_stop))

    if _start > 0:
        pipeline.append(ops.skip(_start))
    elif _start < 0:
        pipeline.append(ops.take_last(-_start))

    if _stop < 0:
        pipeline.append(ops.skip_last(-_stop))

    if _step > 1:
        pipeline.append(ops.filter_indexed(lambda x, i: i % _step == 0))

    return source.pipe(*pipeline)


def _slice_mixed_bounds(
    source: Observable[_T], start: int, stop: int, step: int
) -> Observable[_T]:
    def factory(_: abc.SchedulerBase) -> Observable[_T]:
        def before_stop(item: tuple[_T, int]) -> bool:
            return item[1] < stop

        def discard_index(item: tuple[_T, int]) -> _T:
            return item[0]

        # Keep source indices until the tail is known. Taking the positive
        # stop first would make the negative start relative to that prefix.
        tail = source.pipe(
            ops.map_indexed(lambda value, index: (value, index)),
            ops.take_last(-start),
            ops.take_while(before_stop),
            ops.map(discard_index),
        )
        if step > 1:
            return tail.pipe(ops.filter_indexed(lambda value, index: index % step == 0))
        return tail

    # The generated indices must restart for each subscription.
    return defer(factory)


__all__ = ["slice_"]
