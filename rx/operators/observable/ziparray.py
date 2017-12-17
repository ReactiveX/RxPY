from rx.core import ObservableBase
from rx.internal import extensionclassmethod
from .zip import zip


@extensionclassmethod(ObservableBase, alias="zip_array")
def zip_list(cls, *args):
    """Merge the specified observable sequences into one observable
    sequence by emitting a list with the elements of the observable
    sequences at corresponding indexes.

    Keyword arguments:
    :param Observable cls: Class
    :param Tuple args: Observable sources.

    :return: Returns an observable sequence containing lists of
    elements at corresponding indexes.
    :rtype: Observable
    """

    def result(*args):
        return list(args)

    args += (result,)
    return zip(*args)
