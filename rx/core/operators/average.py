from typing import Callable

from rx import operators
from rx.core import Observable


class AverageValue(object):
    def __init__(self, sum, count):
        self.sum = sum
        self.count = count


def average(key_mapper=None) -> Callable[[Observable], Observable]:
    """Computes the average of an observable sequence of values that are in
    the sequence or obtained by invoking a transform function on each
    element of the input sequence if present.

    Examples:
        >>> res = average()(source)
        >>> res = average(lambda x: x.value)(source)

    Args:
        key_mapper -- A transform function to apply to each element.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element with the
        average of the sequence of values.
    """

    def partial(source: Observable) -> Observable:
        if key_mapper:
            return source.pipe(
                operators.map(key_mapper),
                operators.average()
            )

        def accumulator(prev, cur):
            return AverageValue(sum=prev.sum+cur, count=prev.count+1)

        def mapper(s):
            if s.count == 0:
                raise Exception('The input sequence was empty')

            return s.sum / float(s.count)

        seed = AverageValue(sum=0, count=0)
        return source.pipe(
            operators.scan(accumulator, seed),
            operators.last(),
            operators.map(mapper)
        )
    return partial
