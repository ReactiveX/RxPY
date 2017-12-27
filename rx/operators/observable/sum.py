from rx.core import ObservableBase
from rx.core.typing import Mapper


def sum(source, key_mapper: Mapper = None) -> ObservableBase:
    """Computes the sum of a sequence of values that are obtained by
    invoking an optional transform function on each element of the input
    sequence, else if not specified computes the sum on each item in the
    sequence.

    Example
    res = source.sum()
    res = source.sum(lambda x: x.value)

    key_mapper -- [Optional] A transform function to apply to each
        element.

    Returns an observable sequence containing a single element with the
    sum of the values in the source sequence.
    """

    if key_mapper:
        return source.map(key_mapper).sum()
    else:
        return source.reduce(seed=0, accumulator=lambda prev, curr: prev + curr)
