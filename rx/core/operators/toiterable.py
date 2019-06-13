from typing import Callable, Optional
from rx.core import Observable, typing


def _to_iterable() -> Callable[[Observable], Observable]:
    def to_iterable(source: Observable) -> Observable:
        """Creates an iterable from an observable sequence.

        Returns:
            An observable sequence containing a single element with an
            iterable containing all the elements of the source
            sequence.
        """

        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            nonlocal source

            queue = []

            def on_next(item):
                queue.append(item)

            def on_completed():
                observer.on_next(queue)
                observer.on_completed()

            return source.subscribe(
                on_next,
                observer.on_error,
                on_completed,
                scheduler=scheduler
            )
        return Observable(subscribe_observer=subscribe_observer)
    return to_iterable
