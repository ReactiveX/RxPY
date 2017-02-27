from rx.core import Observable
from rx.internal import extensionmethod


@extensionmethod(Observable, alias="to_iterable")
def to_list(self):
    """Creates a list from an observable sequence.

    Returns an observable sequence containing a single element with a list
    containing all the elements of the source sequence."""

    def accumulator(res, i):
        res.append(i)
        return res[:]

    return self.scan(accumulator, seed=[]).start_with([]).last()


@extensionmethod(Observable)
def to_sorted_list(self, key_selector=None):
    if key_selector:
        return self.to_list().do_action(on_next=lambda l: l.sort(key=key_selector))
    else:
        return self.to_list().map(lambda l: sorted(l))
