from typing import Callable
from rx.core import ObservableBase
from rx.core.typing import Predicate

from .map import map
from .filter import filter
from .some import some


def all(predicate: Predicate) -> Callable[[ObservableBase], ObservableBase]:  # pylint: disable=W0622
    """Determines whether all elements of an observable sequence satisfy a
    condition.

    1 - res = source.all(lambda value: value.length > 3)

    Keyword arguments:
    predicate -- A function to test each element for a condition.

    Returns an observable sequence containing a single element determining
    whether all elements in the source sequence pass the test in the
    specified predicate.
    """

    def partial(source: ObservableBase) -> ObservableBase:
        return source.pipe(
            filter(lambda v: not predicate(v)),
            some(),
            map(lambda b: not b)
        )
    return partial
