from typing import Callable, Iterable, Optional

import rx
from rx.core import Observable, typing


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

        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            def on_next(left):
                try:
                    right = next(second)
                except StopIteration:
                    observer.on_completed()
                else:
                    result = (left, right)
                    observer.on_next(result)

            return first.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler=scheduler
            )
        return Observable(subscribe_observer=subscribe_observer)
    return zip_with_iterable
