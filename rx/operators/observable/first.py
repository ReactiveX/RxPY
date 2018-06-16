from rx.core import ObservableBase

from .firstordefault import first_or_default_async


def first(source, predicate=None) -> ObservableBase:
    """Returns the first element of an observable sequence that
    satisfies the condition in the predicate if present else the first
    item in the sequence.

    Example:
    res = res = source.first()
    res = res = source.first(lambda x: x > 3)

    Keyword arguments:
    source -- Observable sequence.
    predicate -- [Optional] A predicate function to evaluate for
        elements in the source sequence.

    Returns Observable sequence containing the first element in the
    observable sequence that satisfies the condition in the predicate if
    provided, else the first item in the sequence.
    """

    return source.filter(predicate).first() if predicate else first_or_default_async(source, False)
