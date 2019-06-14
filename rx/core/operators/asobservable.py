from typing import Callable, Optional

from rx.core import Observable, typing


def _as_observable() -> Callable[[Observable], Observable]:
    def as_observable(source: Observable) -> Observable:
        """Hides the identity of an observable sequence.

        Args:
            source: Observable source to hide identity from.

        Returns:
            An observable sequence that hides the identity of the
            source sequence.
        """

        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            return observer.subscribe_to(source, scheduler=scheduler)

        return Observable(subscribe_observer=subscribe_observer)
    return as_observable
