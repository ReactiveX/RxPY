from rx.core import Observable


def start_with(self, *args) -> Observable:
    """Prepends a sequence of values to an observable sequence.

    1 - source.start_with(1, 2, 3)

    Returns the source sequence prepended with the specified values.
    """

    sequence = [Observable.from_(args), self]
    return Observable.concat(sequence)
