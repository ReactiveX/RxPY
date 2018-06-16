from typing import Any

from rx.core import ObservableBase
from rx.internal.basic import default_comparer


def contains(source: ObservableBase, value: Any, comparer=None) -> ObservableBase:
    """Determines whether an observable sequence contains a specified
    element with an optional equality comparer.

    Example
    1 - res = source.contains(42)
    2 - res = source.contains({ "value": 42 }, lambda x, y: x["value"] == y["value")

    Keyword parameters:
    source -- Observable sequence.
    value -- The value to locate in the source sequence.
    comparer -- [Optional] An equality comparer to compare elements.

    Returns an observable  sequence containing a single element
    determining whether the source sequence contains an element that has
    the specified value.
    """

    comparer = comparer or default_comparer
    return source.filter(lambda v: comparer(v, value)).some()