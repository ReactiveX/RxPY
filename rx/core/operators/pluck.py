from typing import Any, Callable

from rx import operators as ops
from rx.core import Observable


def _pluck(key: Any) -> Callable[[Observable], Observable]:
    """Retrieves the value of a specified key using dict-like access (as in
    element[key]) from all elements in the Observable sequence.

    Args:
        key: The key to pluck.

    Returns a new Observable {Observable} sequence of key values.

    To pluck an attribute of each element, use pluck_attr.
    """

    return ops.map(lambda x: x[key])


def _pluck_attr(prop: str) -> Callable[[Observable], Observable]:
    """Retrieves the value of a specified property (using getattr) from
    all elements in the Observable sequence.

    Args:
        property: The property to pluck.

    Returns a new Observable {Observable} sequence of property values.

    To pluck values using dict-like access (as in element[key]) on each
    element, use pluck.
    """

    return ops.map(lambda x: getattr(x, prop))
