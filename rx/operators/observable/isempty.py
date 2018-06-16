from rx.core import ObservableBase


def is_empty(self) -> ObservableBase:
    """Determines whether an observable sequence is empty.

    Returns an observable {Observable} sequence containing a single element
    determining whether the source sequence is empty.
    """

    return self.some().map(lambda b: not b)
