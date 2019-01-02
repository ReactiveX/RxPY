from typing import Callable

from rx import operators
from rx.core import Observable
from rx.core.typing import Predicate


def all(predicate: Predicate) -> Callable[[Observable], Observable]:  # pylint: disable=W0622
    """Determines whether all elements of an observable sequence satisfy a
    condition.

    Example:
        >>> op = all(lambda value: value.length > 3)

    Args:
        predicate -- A function to test each element for a condition.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element determining
        whether all elements in the source sequence pass the test in the
        specified predicate.
    """

    filtering = operators.filter(lambda v: not predicate(v))
    mapping = operators.map(lambda b: not b)
    some = operators.some()

    def partial(source: Observable) -> Observable:
        return source.pipe(
            filtering,
            some,
            mapping
        )
    return partial
