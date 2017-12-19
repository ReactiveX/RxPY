from rx.internal import noop
from rx.core import ObservableBase, AnonymousObservable
from rx.disposables import CompositeDisposable
from rx.internal import extensionmethod


@extensionmethod(ObservableBase)
def take_until(self, other):
    """Returns the values from the source observable sequence until the
    other observable sequence produces a value.

    Keyword arguments:
    other -- Observable sequence that terminates propagation of elements of
        the source sequence.

    Returns an observable sequence containing the elements of the source
    sequence up to the point the other sequence interrupted further
    propagation.
    """

    source = self
    other = Observable.from_future(other)

    def subscribe(observer, scheduler=None):

        def close(x):
            observer.close()

        return CompositeDisposable(
            source.subscribe(observer),
            other.subscribe_callbacks(close, observer.throw, noop, scheduler)
        )
    return AnonymousObservable(subscribe)


