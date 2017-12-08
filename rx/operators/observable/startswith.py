from rx.core import Observable
from .concat import concat


def start_with(self, *args) -> Observable:
    """Prepends a sequence of values to an observable sequence.

    1 - source.start_with(1, 2, 3)

    Returns the source sequence prepended with the specified values.
    """

    source = self
    sequence = [Observable.from_(args), source]
    return concat(*sequence)
