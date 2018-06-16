from rx.core import ObservableBase

from .elementatordefault import _element_at_or_default


def element_at(source: ObservableBase, index: int) -> ObservableBase:
    """Returns the element at a specified index in a sequence.

    Example:
    res = source.element_at(5)

    Keyword arguments:
    index -- The zero-based index of the element to retrieve.

    Returns an observable  sequence that produces the element at the
    specified position in the source sequence.
    """

    return _element_at_or_default(source, index, False)
