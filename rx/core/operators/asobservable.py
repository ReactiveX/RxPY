from typing import Callable
from rx.core import Observable, AnonymousObservable


def _as_observable() -> Callable[[Observable], Observable]:
    def as_observable(source: Observable) -> Observable:
        """Hides the identity of an observable sequence.

        Args:
            source: Observable source to hide identity from.

        Returns:
            An observable sequence that hides the identity of the
            source sequence.
        """

        def subscribe(observer, scheduler=None):
            return source.subscribe(observer, scheduler)

        return AnonymousObservable(subscribe)
    return as_observable
