from typing import Callable
from rx.core import Observable
from rx.core.typing import Mapper


def sum(key_mapper: Mapper = None) -> Callable[[Observable], Observable]:
    """Computes the sum of a sequence of values that are obtained by
    invoking an optional transform function on each element of the input
    sequence, else if not specified computes the sum on each item in the
    sequence.

    Example
    res = sum()(source)
    res = sum(lambda x: x.value)(source)

    key_mapper -- [Optional] A transform function to apply to each
        element.

    Returns:
        An function that takes a source observable and returns an
        observable sequence containing a single element with the sum of
        the values in the source sequence.
    """

    def partial(source: Observable) -> Observable:
        if key_mapper:
            return source.map(key_mapper).sum()

        return source.reduce(seed=0, accumulator=lambda prev, curr: prev + curr)
    return partial
