from rx.core import Observable, AnonymousObservable
from rx.disposables import CompositeDisposable, \
    SingleAssignmentDisposable, SerialDisposable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def switch_latest(self):
    """Transforms an observable sequence of observable sequences into an
    observable sequence producing values only from the most recent
    observable sequence.

    :returns: The observable sequence that at any point in time produces the
    elements of the most recent inner observable sequence that has been
    received.
    :rtype: Observable
    """

    sources = self

    def subscribe(observer, scheduler=None):
        has_latest = [False]
        inner_subscription = SerialDisposable()
        is_stopped = [False]
        latest = [0]

        def send(inner_source):
            d = SingleAssignmentDisposable()
            with self.lock:
                latest[0] += 1
                _id = latest[0]
            has_latest[0] = True
            inner_subscription.disposable = d

            # Check if Future or Observable
            inner_source = Observable.from_future(inner_source)

            def send(x):
                if latest[0] == _id:
                    observer.send(x)

            def throw(e):
                if latest[0] == _id:
                    observer.throw(e)

            def close():
                if latest[0] == _id:
                    has_latest[0] = False
                    if is_stopped[0]:
                        observer.close()

            d.disposable = inner_source.subscribe_callbacks(send, throw, close)

        def close():
            is_stopped[0] = True
            if not has_latest[0]:
                observer.close()

        subscription = sources.subscribe_callbacks(send, observer.throw, close)
        return CompositeDisposable(subscription, inner_subscription)
    return AnonymousObservable(subscribe)
