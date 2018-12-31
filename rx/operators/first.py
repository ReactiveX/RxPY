from typing import Callable
from rx.core import ObservableBase as Observable

from .firstordefault import first_or_default_async


def first(predicate=None) -> Callable[[Observable], Observable]:
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

    def partial(source: Observable) -> Observable:
        return source.filter(predicate).first() if predicate else first_or_default_async(source, False)
    return partial
