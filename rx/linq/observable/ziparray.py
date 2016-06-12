from rx.core import Observable
from rx.internal import extensionclassmethod


@extensionclassmethod(Observable, alias="zip_array")
def zip_list(cls, *args):
    """Merge the specified observable sequences into one observable
    sequence by emitting a list with the elements of the observable
    sequences at corresponding indexes.

    Arguments:
      args (Tuple): Observable sources.

    Returns:
      Observable: Returns an observable sequence containing lists of
      elements at corresponding indexes.    
    """
    def result(*args):
        return list(args)

    args += (result,)
    return Observable.zip(*args)
