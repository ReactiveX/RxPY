from typing import Callable
from rx.core import ObservableBase, AnonymousObservable, Disposable


def finally_action(source: ObservableBase, action: Callable) -> ObservableBase:
    """Invokes a specified action after the source observable sequence
    terminates gracefully or exceptionally.

    Example:
    res = observable.finally(lambda: print('sequence ended')

    Keyword arguments:
    source -- Observable sequence.
    action -- Action to invoke after the source observable sequence
        terminates.

    Returns observable sequence with the action-invoking termination
    behavior applied.
    """

    def subscribe(observer, scheduler=None):
        try:
            subscription = source.subscribe(observer, scheduler)
        except Exception:
            action()
            raise

        def dispose():
            try:
                subscription.dispose()
            finally:
                action()

        return Disposable.create(dispose)
    return AnonymousObservable(subscribe)
