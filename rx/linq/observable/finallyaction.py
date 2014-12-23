from rx import Observable, AnonymousObservable
from rx.disposables import Disposable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def finally_action(self, action):
    """Invokes a specified action after the source observable sequence
    terminates gracefully or exceptionally.

    Example:
    res = observable.finally(lambda: print('sequence ended')

    Keyword arguments:
    action -- {Function} Action to invoke after the source observable
        sequence terminates.
    Returns {Observable} Source sequence with the action-invoking
    termination behavior applied.
    """

    source = self

    def subscribe(observer):
        try:
            subscription = source.subscribe(observer)
        except Exception as ex:
            action()
            raise

        def dispose():
            try:
                subscription.dispose()
            finally:
                action()

        return Disposable(dispose)
    return AnonymousObservable(subscribe)
