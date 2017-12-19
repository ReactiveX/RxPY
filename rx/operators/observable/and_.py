from rx.core import ObservableBase

from rx.joins import Pattern


def and_(self, right):
    """Creates a pattern that matches when both observable sequences
    have an available value.

    :param Observable right: Observable sequence to match with the
        current sequence.
    :returns: Pattern object that matches when both observable sequences
        have an available value.
    """

    return Pattern([self, right])
