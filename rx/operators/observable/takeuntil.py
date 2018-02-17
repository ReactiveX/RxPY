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

        def on_completed(_):
            observer.on_completed()

        return CompositeDisposable(
            source.subscribe(observer),
            other.subscribe_(on_completed, observer.on_error, noop, scheduler)
        )
    return AnonymousObservable(subscribe)