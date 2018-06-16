from rx.core import ObservableBase
from rx.internal.basic import default_sub_comparer

from .minby import extrema_by

def max_by(soure, key_mapper, comparer=None) -> ObservableBase:
    """Returns the elements in an observable sequence with the maximum
    key value according to the specified comparer.

    Example
    res = source.max_by(lambda x: x.value)
    res = source.max_by(lambda x: x.value, lambda x, y: x - y)

    Keyword arguments:
    key_mapper -- {Function} Key mapper function.
    comparer -- {Function} [Optional] Comparer used to compare key values.

    Returns an observable {Observable} sequence containing a list of zero
    or more elements that have a maximum key value.
    """

    comparer = comparer or default_sub_comparer
    return extrema_by(soure, key_mapper, comparer)
