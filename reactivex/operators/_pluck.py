from typing import Any, Callable, Dict, TypeVar

from reactivex import Observable
from reactivex import operators as ops

_TKey = TypeVar("_TKey")
_TValue = TypeVar("_TValue")


def pluck_(
    key: _TKey,
) -> Callable[[Observable[Dict[_TKey, _TValue]]], Observable[_TValue]]:
    """Retrieves the value of a specified key using dict-like access (as in
    element[key]) from all elements in the Observable sequence.

    Args:
        key: The key to pluck.

    Returns a new Observable {Observable} sequence of key values.

    To pluck an attribute of each element, use pluck_attr.
    """

    def mapper(x: Dict[_TKey, _TValue]) -> _TValue:
        return x[key]

    return ops.map(mapper)


def pluck_attr_(prop: str) -> Callable[[Observable[Any]], Observable[Any]]:
    """Retrieves the value of a specified property (using getattr) from
    all elements in the Observable sequence.

    Args:
        property: The property to pluck.

    Returns a new Observable {Observable} sequence of property values.

    To pluck values using dict-like access (as in element[key]) on each
    element, use pluck.
    """

    return ops.map(lambda x: getattr(x, prop))


__all__ = ["pluck_", "pluck_attr_"]
