from typing import Callable

from rx import operators as ops
from rx.core import Observable
from rx.core.typing import Mapper


# pylint: disable=redefined-builtin
def _sum(key_mapper: Mapper = None) -> Callable[[Observable], Observable]:

    reducing = ops.reduce(seed=0, accumulator=lambda prev, curr: prev + curr)

    def sum(source: Observable) -> Observable:
        """Computes the sum of a sequence of values that are obtained
        by invoking an optional transform function on each element of
        the input sequence, else if not specified computes the sum on
        each item in the sequence.

        Example:
            res = sum(source)

        Args:
            key_mapper -- [Optional] A transform function to apply to
                each element.

        Returns:
            An observable sequence containing a single element with the
            sum of the values in the source sequence.
        """
        if key_mapper:
            mapping = ops.map(key_mapper)
            summing = ops.sum()

            return source.pipe(
                mapping,
                summing
            )

        return source.pipe(reducing)
    return sum
