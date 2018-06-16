from rx.core import ObservableBase

from .lastordefault import last_or_default_async


def last(source, predicate=None) -> ObservableBase:
    """Returns the last element of an observable sequence that satisfies the
    condition in the predicate if specified, else the last element.

    Example:
    res = source.last()
    res = source.last(lambda x: x > 3)

    Keyword arguments:
    source - Observable sequence.
    predicate -- [Optional] A predicate function to evaluate for
        elements in the source sequence.

    Returns sequence containing the last element in the observable
    sequence that satisfies the condition in the predicate.
    """

    return source.filter(predicate).last() if predicate else last_or_default_async(source, False)
