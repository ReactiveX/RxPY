from typing import Callable
from rx.core import Observable

from rx import operators


def count(predicate=None) -> Callable[[Observable], Observable]:
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

    filtering = operators.count(predicate)
    counter = operators.reduce(lambda count, _: count + 1, seed=0)

    def partial(source: Observable) -> Observable:
        if predicate:
            return source.pipe(filtering, count())

        return source.pipe(counter)
    return partial
