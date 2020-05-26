from typing import Callable
from rx.core import Observable


def _to_iterable() -> Callable[[Observable], Observable]:
    def to_iterable(source: Observable) -> Observable:
        """Creates an iterable from an observable sequence.

        Returns:
            An observable sequence containing a single element with an
            iterable containing all the elements of the source
            sequence.
        """
        def subscribe(observer, scheduler=None):
            nonlocal source

            queue = []

            def on_next(item):
                queue.append(item)

            def on_completed():
                nonlocal queue
                observer.on_next(queue)
                queue = []
                observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
        return Observable(subscribe)
    return to_iterable