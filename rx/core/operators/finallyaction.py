from typing import Callable

from rx import disposable
from rx.core import Observable, AnonymousObservable


def _finally_action(action: Callable) -> Callable[[Observable], Observable]:
    def finally_action(source: Observable) -> Observable:
        """Invokes a specified action after the source observable
        sequence terminates gracefully or exceptionally.

        Example:
            res = finally(source)

        Args:
            source: Observable sequence.

        Returns:
            An observable sequence with the action-invoking termination
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

            return disposable.create(dispose)
        return AnonymousObservable(subscribe)
    return finally_action
