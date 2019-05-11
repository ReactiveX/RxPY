from typing import Callable, Optional

from rx import operators as ops
from rx.core import Observable, pipe
from rx.core.typing import Predicate


def _single(predicate: Optional[Predicate] = None) -> Callable[[Observable], Observable]:
    """Returns the only element of an observable sequence that satisfies the
    condition in the optional predicate, and reports an exception if there
    is not exactly one element in the observable sequence.

    Example:
        >>> res = single()
        >>> res = single(lambda x: x == 42)

    Args:
        predicate -- [Optional] A predicate function to evaluate for
            elements in the source sequence.

    Returns:
        An observable sequence containing the single element in the
        observable sequence that satisfies the condition in the predicate.
    """

    if predicate:
        return pipe(ops.filter(predicate), ops.single())
    else:
        return ops.single_or_default_async(False)
