from rx.core import ObservableBase, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal import extensionmethod


@extensionmethod(ObservableBase)
def skip_until(self, other):
    """Returns the values from the source observable sequence only after
    the other observable sequence produces a value.

    other -- The observable sequence that triggers propagation of elements
        of the source sequence.

    Returns an observable sequence containing the elements of the source
    sequence starting from the point the other sequence triggered
    propagation.
    """

    source = self
    other = Observable.from_future(other)

    def subscribe(observer, scheduler=None):
        is_open = [False]

        def send(left):
            if is_open[0]:
                observer.send(left)

        def close():
            if is_open[0]:
                observer.close()

        subs = source.subscribe_callbacks(send, observer.throw, close, scheduler)
        disposables = CompositeDisposable(subs)

        right_subscription = SingleAssignmentDisposable()
        disposables.add(right_subscription)

        def send2(x):
            is_open[0] = True
            right_subscription.dispose()

        def close2():
            right_subscription.dispose()

        right_subscription.disposable = other.subscribe_callbacks(send2, observer.throw, close2, scheduler)

        return disposables
    return AnonymousObservable(subscribe)
