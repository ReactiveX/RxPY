from rx.core import Observable

from .some import some
from .map import map


def is_empty(source: Observable) -> Observable:
    """Determines whether an observable sequence is empty.

    Returns:
        An observable sequence containing a single element
        determining whether the source sequence is empty.
    """

    return source.pipe(
        some(),
        map(lambda b: not b)
    )
