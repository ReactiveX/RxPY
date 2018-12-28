from typing import Any, Callable

from rx.core import ObservableBase as Observable
from rx.internal.basic import default_comparer


def contains(value: Any, comparer=None) -> Callable[[Observable], Observable]:
    """Determines whether an observable sequence contains a specified
    element with an optional equality comparer.

    Examples:
        >>> res = contains(42)(sournce)
        >>> res = contains({ "value": 42 }, lambda x, y: x["value"] == y["value")(source)

    Args:
        value -- The value to locate in the source sequence.
        comparer -- [Optional] An equality comparer to compare elements.

    Returns:
        A function that takes a source observable that returns an
        observable  sequence containing a single element determining
        whether the source sequence contains an element that has the
        specified value.
    """

    def partial(source: Observable) -> Observable:
        comparer_ = comparer or default_comparer
        return source.filter(lambda v: comparer_(v, value)).some()
    return partial
