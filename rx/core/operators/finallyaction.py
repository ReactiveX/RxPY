from typing import Callable, Optional

from rx.disposable import Disposable
from rx.core import Observable, typing


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

        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            try:
                subscription = source.subscribe_observer(observer, scheduler=scheduler)
            except Exception:
                action()
                raise

            def dispose():
                try:
                    subscription.dispose()
                finally:
                    action()

            return Disposable(dispose)
        return Observable(subscribe_observer=subscribe_observer)
    return finally_action
