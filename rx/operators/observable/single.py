from rx.core import ObservableBase
from rx.core.typing import Predicate
from .singleordefault import single_or_default_async


def single(source: ObservableBase, predicate: Predicate = None) -> ObservableBase:
    """Returns the only element of an observable sequence that satisfies the
    condition in the optional predicate, and reports an exception if there
    is not exactly one element in the observable sequence.

    Example:
    res = source.single()
    res = source.single(lambda x: x == 42)

    Keyword arguments:
    predicate -- [Optional] A predicate function to evaluate for
        elements in the source sequence.

    Returns observable sequence containing the single element in the
    observable sequence that satisfies the condition in the predicate.
    """

    return source.filter(predicate).single() if predicate else \
        single_or_default_async(source, False)
