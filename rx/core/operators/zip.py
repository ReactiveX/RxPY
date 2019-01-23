from typing import Callable

import rx
from rx.core import Observable, AnonymousObservable


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
        sources = [source] + list(args)
        return rx.zip(*sources)
    return zip

def _zip_with_iterable(second):
    def zip_with_iterable(source: Observable) -> Observable:
        """Merges the specified observable sequence and list into one
        observable sequence by creating a tuple whenever all of
        the observable sequences have produced an element at a
        corresponding index.

        Example
            >>> res = zip(xs, [1,2,3])

        Args:
            source -- Source observable to zip.

        Returns:
            An observable sequence containing the result of
            combining elements of the sources as a tuple.
        """

        first = source

        def subscribe(observer, scheduler=None):
            length = len(second)
            index = 0

            def on_next(left):
                nonlocal index

                if index < length:
                    right = second[index]
                    index += 1
                    result = (left, right)
                    observer.on_next(result)
                else:
                    observer.on_completed()

            return first.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return zip_with_iterable
