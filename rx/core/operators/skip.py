from typing import Callable

from rx.core import Observable
from rx.internal import ArgumentOutOfRangeException


def _skip(count: int) -> Callable[[Observable], Observable]:
    if count < 0:
        raise ArgumentOutOfRangeException()

    def skip(source: Observable) -> Observable:
        """The skip operator.

        Bypasses a specified number of elements in an observable sequence
        and then returns the remaining elements.

        Args:
            source: The source observable.

        Returns:
            An observable sequence that contains the elements that occur
            after the specified index in the input sequence.
        """

        def subscribe(observer, scheduler=None):
            remaining = count

            def on_next(value):
                nonlocal remaining

                if remaining <= 0:
                    observer.on_next(value)
                else:
                    remaining -= 1

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return Observable(subscribe)
    return skip
