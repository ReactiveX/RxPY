from typing import Callable
from rx.core import ObservableBase

from .scan import scan
from .map import map
from .last import last


class AverageValue(object):
    def __init__(self, sum, count):
        self.sum = sum
        self.count = count


def average(key_mapper=None) -> Callable[[ObservableBase], ObservableBase]:
    """Computes the average of an observable sequence of values that are in
    the sequence or obtained by invoking a transform function on each
    element of the input sequence if present.

    Examples:
        >>> res = average()(source)
        >>> res = average(lambda x: x.value)(source)

    Args:
        key_mapper -- A transform function to apply to each element.

    Returns:
        An observable sequence containing a single element with the
        average of the sequence of values.
    """

    def partial(source: ObservableBase) -> ObservableBase:
        if key_mapper:
            return source.map(key_mapper).average()

        def accumulator(prev, cur):
            return AverageValue(sum=prev.sum+cur, count=prev.count+1)

        def mapper(s):
            if s.count == 0:
                raise Exception('The input sequence was empty')

            return s.sum / float(s.count)

        seed = AverageValue(sum=0, count=0)
        return source.pipe(
            scan(accumulator, seed),
            last(),
            map(mapper)
        )
    return partial
