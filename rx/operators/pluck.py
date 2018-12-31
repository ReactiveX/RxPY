from typing import Any
from rx.core import ObservableBase


def pluck(source: ObservableBase, key: Any) -> ObservableBase:
    """Retrieves the value of a specified key using dict-like access (as in
    element[key]) from all elements in the Observable sequence.

    Keyword arguments:
    key -- The key to pluck.

    Returns a new Observable {Observable} sequence of key values.

    To pluck an attribute of each element, use pluck_attr.

    """

    return source.map(lambda x: x[key])


def pluck_attr(source: ObservableBase, prop: str) -> ObservableBase:
    """Retrieves the value of a specified property (using getattr) from
    all elements in the Observable sequence.

    Keyword arguments:
    property -- The property to pluck.

    Returns a new Observable {Observable} sequence of property values.

    To pluck values using dict-like access (as in element[key]) on each
    element, use pluck.

    """

    return source.map(lambda x: getattr(x, prop))
