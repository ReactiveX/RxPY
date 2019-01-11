from typing import Callable

from rx import operators as ops
from rx.core import Observable, pipe
from rx.internal.basic import identity
from rx.internal.exceptions import SequenceContainsNoElementsError


def first_only(x):
    if not x:
        raise SequenceContainsNoElementsError()

    return x[0]


def _min(comparer: Callable = None) -> Callable[[Observable], Observable]:
    """The `min` operator.

    Returns the minimum element in an observable sequence according to
    the optional comparer else a default greater than less than check.

    Examples:
        >>> res = source.min()
        >>> res = source.min(lambda x, y: x.value - y.value)

    Args:
        comparer: [Optional] Comparer used to compare elements.

    Returns:
        An observable sequence containing a single element
        with the minimum element in the source sequence.
    """

    return pipe(
        ops.min_by(identity, comparer),
        ops.map(first_only)
    )
