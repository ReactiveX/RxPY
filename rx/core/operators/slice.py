from typing import Callable, Optional

from rx import operators as ops
from rx.core import Observable


# pylint: disable=redefined-builtin
def _slice(start: Optional[int] = None, stop: Optional[int] = None, step: int = 1) -> Callable[[Observable], Observable]:
    has_start = start is not None
    has_stop = stop is not None
    has_step = step is not None

    pipeline = []

    def slice(source: Observable) -> Observable:
        """The partially applied slice operator.

        Slices the given observable. It is basically a wrapper around the
        operators skip(), skip_last(), take(), take_last() and filter().

        This marble diagram helps you remember how slices works with streams.
        Positive numbers is relative to the start of the events, while negative
        numbers are relative to the end (close) of the stream.

         r---e---a---c---t---i---v---e---|
         0   1   2   3   4   5   6   7   8
        -8  -7  -6  -5  -4  -3  -2  -1   0

        Examples:
            >>> result = source.slice(1, 10)
            >>> result = source.slice(1, -2)
            >>> result = source.slice(1, -1, 2)

        Args:
            source: Observable to slice

        Returns:
            A sliced observable sequence.
        """

        if has_stop and stop >= 0:
            pipeline.append(ops.take(stop))

        if has_start and start > 0:
            pipeline.append(ops.skip(start))

        if has_start and start < 0:
            pipeline.append(ops.take_last(abs(start)))

        if has_stop and stop < 0:
            pipeline.append(ops.skip_last(abs(stop)))

        if has_step:
            if step > 1:
                pipeline.append(ops.filter_indexed(lambda x, i: i % step == 0))
            elif step < 0:
                # Reversing events is not supported
                raise TypeError("Negative step not supported.")

        return source.pipe(*pipeline)
    return slice
