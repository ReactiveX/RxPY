from typing import Callable, Iterable

import rx
from rx.core import Observable

# pylint: disable=redefined-builtin
def _zip(*args: Observable) -> Callable[[Observable], Observable]:
    def zip(source: Observable) -> Observable:
        """Merges the specified observable sequences into one observable
        sequence by creating a tuple whenever all of the
        observable sequences have produced an element at a corresponding
        index.

        Example:
            >>> res = zip(source)

        Args:
            source: Source observable to zip.

        Returns:
            An observable sequence containing the result of combining
            elements of the sources as a tuple.
        """
        return rx.zip(source, *args)
    return zip

def _zip_with_iterable(seq: Iterable) -> Callable[[Observable], Observable]:
    def zip_with_iterable(source: Observable) -> Observable:
        """Merges the specified observable sequence and list into one
        observable sequence by creating a tuple whenever all of
        the observable sequences have produced an element at a
        corresponding index.

        Example
            >>> res = zip(source)

        Args:
            source: Source observable to zip.

        Returns:
            An observable sequence containing the result of combining
            elements of the sources as a tuple.
        """

        first = source
        second = iter(seq)

        def subscribe(observer, scheduler=None):
            index = 0

            def on_next(left):
                nonlocal index

                try:
                    right = next(second)
                except StopIteration:
                    observer.on_completed()
                else:
                    result = (left, right)
                    observer.on_next(result)

            return first.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return Observable(subscribe)
    return zip_with_iterable
