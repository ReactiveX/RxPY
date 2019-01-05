from typing import Callable
from rx.core import Observable
from rx.core.typing import Predicate

from rx import operators as _


def _count(predicate: Predicate = None) -> Callable[[Observable], Observable]:
    """Returns an observable sequence containing a value that represents
    how many elements in the specified observable sequence satisfy a
    condition if provided, else the count of items.

    Examples:
        >>> res = count()
        >>> res = count(lambda x: x > 3)

    Args:
        predicate -- A function to test each element for a condition.

    Returns:
        An operator function that takes an observable source and returns
        an observable sequence containing a single element with a number
        that represents how many elements in the input sequence satisfy
        the condition in the predicate function if provided, else
        the count of items in the sequence.
    """

    counter = _.reduce(lambda n, _: n + 1, seed=0)

    def count(source: Observable) -> Observable:
        if predicate:
            filtering = _.filter(predicate)
            return source.pipe(filtering, _.count())

        return source.pipe(counter)
    return count
