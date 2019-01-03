from typing import Any, Callable

from rx import from_iterable
from rx.core import Observable

from .concat import concat


def start_with(*args: Any) -> Callable[[Observable], Observable]:
    """Prepends a sequence of values to an observable sequence.

    Example:
        >>> start_with(1, 2, 3)

    Returns:
        An operator function that takes a source observable and returns
        the source sequence prepended with the specified values.
    """

    def partial(source: Observable) -> Observable:
        start = from_iterable(args)
        sequence = [start, source]
        return concat(*sequence)
    return partial
