from rx.internal import noop
from rx.core import Observable, ObservableBase, AnonymousObservable
from rx.disposables import CompositeDisposable


def take_until(source: ObservableBase, other: ObservableBase) -> ObservableBase:
    """Returns the values from the source observable sequence until the
    other observable sequence produces a value.

    Keyword arguments:
    other -- Observable sequence that terminates propagation of elements
        of the source sequence.

    Returns an observable sequence containing the elements of the source
    sequence up to the point the other sequence interrupted further
    propagation.
    """

    other = Observable.from_future(other)

    def subscribe(observer, scheduler=None):

        def close(_):
            observer.close()

        return CompositeDisposable(
            source.subscribe(observer),
            other.subscribe_(close, observer.throw, noop, scheduler)
        )
    return AnonymousObservable(subscribe)