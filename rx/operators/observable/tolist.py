from rx.core import ObservableBase
from rx.internal import extensionmethod


@extensionmethod(ObservableBase, alias="to_iterable")
def to_list(self):
    """Creates a list from an observable sequence.

    Returns an observable sequence containing a single element with a list
    containing all the elements of the source sequence."""

    def accumulator(res, item):
        print("****************************** accumulator", item)
        res = res[:]
        res.append(item)
        return res

    return self.do_action(lambda x: print(x)).reduce(accumulator, seed=[])


@extensionmethod(ObservableBase)
def to_sorted_list(self, key_selector=None, reverse=False):
    """
    Creates a sorted list from an observable sequence,
    with an optional key_selector used to map the attribute for sorting

    Returns an observable sequence containing a single element with a list
    containing all the sorted elements of the source sequence."""

    if key_selector:
        return self.to_list().do_action(send=lambda l: l.sort(key=key_selector, reverse=reverse))
    else:
        return self.to_list().do_action(lambda l: l.sort(reverse=reverse))
