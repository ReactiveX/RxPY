from typing import Callable

import rx
from rx.core import Observable, AnonymousObservable
from rx.core.typing import Mapper


def _zip(*args: Observable, result_mapper: Mapper = None) -> Callable[[Observable], Observable]:
    def zip(source: Observable) -> Observable:
        """Merges the specified observable sequences into one observable
        sequence by using the mapper function whenever all of the
        observable sequences have produced an element at a corresponding
        index.

        The last element in the arguments must be a function to invoke for
        each series of elements at corresponding indexes in the sources.

        Example:
            >>> res = zip(source)

        Args:
            source: Source observable to zip.

        Returns:
            An observable sequence containing the result of combining
            elements of the sources using the specified result mapper
            function.
        """
        sources = [source] + list(args)
        return rx.zip(*sources, result_mapper=result_mapper)
    return zip

def _zip_with_iterable(second, result_mapper):
    def zip_with_iterable(source: Observable) -> Observable:
        """Merges the specified observable sequence and list into one
        observable sequence by using the mapper function whenever all of
        the observable sequences have produced an element at a
        corresponding index.

        The result mapper must be a function to invoke for each series of
        elements at corresponding indexes in the sources.

        Example
            >>> res = zip(xs, [1,2,3], result_mapper=fn)

        Args:
            source -- Source observable to zip.

        Returns:
            An observable sequence containing the result of
            combining elements of the sources using the specified result
        mapper function.
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
                    try:
                        result = result_mapper(left, right)
                    except Exception as ex:
                        observer.on_error(ex)
                        return
                    observer.on_next(result)
                else:
                    observer.on_completed()

            return first.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return zip_with_iterable