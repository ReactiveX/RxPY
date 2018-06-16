from rx.core import ObservableBase


def all(source, predicate) -> ObservableBase:
    """Determines whether all elements of an observable sequence satisfy a
    condition.

    1 - res = source.all(lambda value: value.length > 3)

    Keyword arguments:
    predicate -- A function to test each element for a condition.

    Returns an observable sequence containing a single element determining
    whether all elements in the source sequence pass the test in the
    specified predicate.
    """

    return source.filter(lambda v: not predicate(v)).some().map(lambda b: not b)
