from typing import Callable
from rx.core import Observable, AnonymousObservable, Disposable


def finally_action(action: Callable) -> Callable[[Observable], Observable]:
    """Invokes a specified action after the source observable sequence
    terminates gracefully or exceptionally.

    Example:
        res = finally(lambda: print('sequence ended')

    Args:
        source -- Observable sequence.
        action -- Action to invoke after the source observable sequence
            terminates.

    Returns:
        A function that takes an observable source and returns an
        observable sequence with the action-invoking termination
        behavior applied.
    """

    def partial(source: Observable) -> Observable:
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
    return partial
