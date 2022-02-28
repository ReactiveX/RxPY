from typing import Callable, Optional, TypeVar

from reactivex import Observable, abc, typing
from reactivex.disposable import Disposable

_T = TypeVar("_T")


def finally_action_(
    action: typing.Action,
) -> Callable[[Observable[_T]], Observable[_T]]:
    def finally_action(source: Observable[_T]) -> Observable[_T]:
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

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            try:
                subscription = source.subscribe(observer, scheduler=scheduler)
            except Exception:
                action()
                raise

            def dispose():
                try:
                    subscription.dispose()
                finally:
                    action()

            return Disposable(dispose)

        return Observable(subscribe)

    return finally_action


__all__ = ["finally_action_"]
