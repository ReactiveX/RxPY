from rx.core import Observable, AnonymousObservable

from rx.disposables import CompositeDisposable, SingleAssignmentDisposable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def exclusive(self):
    """Performs a exclusive waiting for the first to finish before
    subscribing to another observable. Observables that come in between
    subscriptions will be dropped on the floor.

    Returns an exclusive observable {Observable} with only the results that
    happen when subscribed.
    """

    sources = self

    def subscribe(observer, scheduler=None):
        has_current = [False]
        is_stopped = [False]
        m = SingleAssignmentDisposable()
        g = CompositeDisposable()

        g.add(m)

        def send(inner_source):
            if not has_current[0]:
                has_current[0] = True

                inner_source = Observable.from_future(inner_source)

                inner_subscription = SingleAssignmentDisposable()
                g.add(inner_subscription)

                def close_inner():
                    g.remove(inner_subscription)
                    has_current[0] = False
                    if is_stopped[0] and len(g) == 1:
                        observer.close()

                inner_subscription.disposable = inner_source.subscribe_callbacks(
                    observer.send,
                    observer.throw,
                    close_inner
                )

        def close():
            is_stopped[0] = True
            if not has_current[0] and len(g) == 1:
                observer.close()

        m.disposable = sources.subscribe_callbacks(send, observer.throw, close)
        return g
    return AnonymousObservable(subscribe)
