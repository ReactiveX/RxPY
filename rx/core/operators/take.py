from typing import Callable

from rx import empty
from rx.core import Observable
from rx.internal import ArgumentOutOfRangeException


def _take(count: int) -> Callable[[Observable], Observable]:
    if count < 0:
        raise ArgumentOutOfRangeException()

    def take(source: Observable) -> Observable:
        """Returns a specified number of contiguous elements from the start of
        an observable sequence.

        >>> take(source)

        Keyword arguments:
        count -- The number of elements to return.

        Returns an observable sequence that contains the specified number of
        elements from the start of the input sequence.
        """

        if not count:
            return empty()

        def subscribe(observer, scheduler=None):
            remaining = count

            def on_next(value):
                nonlocal remaining

                if remaining > 0:
                    remaining -= 1
                    observer.on_next(value)
                    if not remaining:
                        observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return Observable(subscribe)
    return take
