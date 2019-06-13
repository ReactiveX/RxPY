from typing import Callable, Optional

from rx.core import Observable, typing


def _dematerialize() -> Callable[[Observable], Observable]:
    def dematerialize(source: Observable) -> Observable:
        """Partially applied dematerialize operator.

        Dematerializes the explicit notification values of an
        observable sequence as implicit notifications.

        Returns:
            An observable sequence exhibiting the behavior
            corresponding to the source sequence's notification values.
        """

        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            def on_next(value):
                return value.accept(observer)

            return source.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler=scheduler
            )
        return Observable(subscribe_observer=subscribe_observer)
    return dematerialize
