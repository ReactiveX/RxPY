from typing import Callable, Optional
from rx import operators as ops
from rx.core import Observable, pipe
from rx.core.typing import Predicate

from .firstordefault import _first_or_default_async


def _first(predicate: Optional[Predicate] = None) -> Callable[[Observable], Observable]:
    """Returns the first element of an observable sequence that
    satisfies the condition in the predicate if present else the first
    item in the sequence.

    Examples:
        >>> res = res = first()(source)
        >>> res = res = first(lambda x: x > 3)(source)

    Args:
        predicate -- [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        A function that takes an observable source and returns an
        observable sequence containing the first element in the
        observable sequence that satisfies the condition in the predicate if
        provided, else the first item in the sequence.
    """

    if predicate:
        return pipe(ops.filter(predicate), ops.first())

    return _first_or_default_async(False)
