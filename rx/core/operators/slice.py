from sys import maxsize
from typing import Callable, Optional

from rx import operators as ops
from rx.core import Observable


# pylint: disable=redefined-builtin
def _slice(start: Optional[int] = None,
           stop: Optional[int] = None,
           step: Optional[int] = None
           ) -> Callable[[Observable], Observable]:
    _start: int = 0 if start is None else start
    _stop: int = maxsize if stop is None else stop
    _step: int = 1 if step is None else step

    pipeline = []

    def slice(source: Observable) -> Observable:
        """The partially applied slice operator.

        Slices the given observable. It is basically a wrapper around the operators
        :func:`skip <rx.operators.skip>`,
        :func:`skip_last <rx.operators.skip_last>`,
        :func:`take <rx.operators.take>`,
        :func:`take_last <rx.operators.take_last>` and
        :func:`filter <rx.operators.filter>`.

        The following diagram helps you remember how slices works with streams.

        Positive numbers are relative to the start of the events, while negative
        numbers are relative to the end (close) of the stream.

        .. code::

            r---e---a---c---t---i---v---e---!
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
        elif _step < 0:
            # Reversing events is not supported
            raise TypeError('Negative step not supported.')

        return source.pipe(*pipeline)
    return slice
