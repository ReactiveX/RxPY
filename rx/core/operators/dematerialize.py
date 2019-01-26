from typing import Callable
from rx.core import Observable


def _dematerialize() -> Callable[[Observable], Observable]:
    def dematerialize(source: Observable) -> Observable:
        """Partially applied dematerialize operator.

        Dematerializes the explicit notification values of an
        observable sequence as implicit notifications.

        Returns:
            An observable sequence exhibiting the behavior
            corresponding to the source sequence's notification values.
        """

        def subscribe(observer, scheduler=None):
            def on_next(value):
                return value.accept(observer)

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return Observable(subscribe)
    return dematerialize
