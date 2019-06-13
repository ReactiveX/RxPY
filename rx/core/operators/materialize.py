from typing import Callable, Optional

from rx.core import Observable, typing
from rx.core.notification import OnNext, OnError, OnCompleted


def _materialize() -> Callable[[Observable], Observable]:
    def materialize(source: Observable) -> Observable:
        """Partially applied materialize operator.

        Materializes the implicit notifications of an observable
        sequence as explicit notification values.

        Args:
            source: Source observable to materialize.

        Returns:
            An observable sequence containing the materialized
            notification values from the source sequence.
        """

        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            def on_next(value):
                observer.on_next(OnNext(value))

            def on_error(exception):
                observer.on_next(OnError(exception))
                observer.on_completed()

            def on_completed():
                observer.on_next(OnCompleted())
                observer.on_completed()

            return source.subscribe(
                on_next,
                on_error,
                on_completed,
                scheduler=scheduler
            )
        return Observable(subscribe_observer=subscribe_observer)
    return materialize
