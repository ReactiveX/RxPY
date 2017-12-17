from rx.core import ObservableBase, AnonymousObservable
from rx.internal import noop
from rx.internal import extensionmethod


@extensionmethod(ObservableBase)
def ignore_elements(self):
    """Ignores all elements in an observable sequence leaving only the
    termination messages.

    Returns an empty observable {Observable} sequence that signals
    termination, successful or exceptional, of the source sequence.
    """

    source = self

    def subscribe(observer, scheduler=None):
        return source.subscribe_callbacks(noop, observer.throw, observer.close, scheduler)

    return AnonymousObservable(subscribe)
