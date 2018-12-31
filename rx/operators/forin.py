from rx.core import ObservableBase, Observable
from rx.internal import Iterable


def for_in(values, result_mapper) -> ObservableBase:
    """Concatenates the observable sequences obtained by running the
    specified result mapper for each element in source.

    Keyword arguments:
    values -- A list of values to turn into an observable
        sequence.
    result_mapper -- A function to apply to each item in the
        values list to turn it into an observable sequence.
    Returns an observable sequence from the concatenated
    observable sequences.
    """

    return Observable.concat(Iterable.for_each(values, result_mapper))
