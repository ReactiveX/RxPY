from rx.core import ObservableBase, AnonymousObservable
from rx.internal import noop


def ignore_elements(source: ObservableBase) -> ObservableBase:
    """Ignores all elements in an observable sequence leaving only the
    termination messages.

    Returns an empty observable {Observable} sequence that signals
    termination, successful or exceptional, of the source sequence.
    """

    def subscribe(observer, scheduler=None):
        return source.subscribe_(noop, observer.throw, observer.close, scheduler)

    return AnonymousObservable(subscribe)
