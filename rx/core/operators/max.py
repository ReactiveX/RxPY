from typing import Callable, Any

from rx import operators as _
from rx.core import Observable
from rx.internal.basic import identity

from .min import first_only


def max(comparer: Callable[[Any], bool] = None) -> Callable[[Observable], Observable]:  # pylint: disable=W0622
    """Returns the maximum value in an observable sequence according to
    the specified comparer.

    Examples:
        >>> op = max()
        >>> op = max(lambda x, y:  x.value - y.value)

    Args:
        comparer -- [Optional] Comparer used to compare elements.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element with the
        maximum element in the source sequence.
    """

    def partial(source: Observable) -> Observable:
        return source.pipe(
            _.max_by(identity, comparer),
            _.map(lambda x: first_only(x))
        )
    return partial
