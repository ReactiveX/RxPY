from typing import Callable
from rx.core import ObservableBase as Observable


def count(predicate=None) -> Callable[[Observable], Observable]:
    """Returns an observable sequence containing a value that represents
    how many elements in the specified observable sequence satisfy a
    condition if provided, else the count of items.

    Examples:
        >>> res = count()(source)
        >>> res = count(lambda x: x > 3)(source)

    Args:
        source -- Observable sequence.
        predicate -- A function to test each element for a condition.

    Returns an observable sequence containing a single element with a
    number that represents how many elements in the input sequence
    satisfy the condition in the predicate function if provided, else
    the count of items in the sequence.
    """

    def partial(source: Observable) -> Observable:
        if predicate:
            return source.filter(predicate).count()

        return source.reduce(lambda count, _: count + 1, seed=0)
    return partial
