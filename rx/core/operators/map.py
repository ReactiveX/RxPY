from typing import Callable, Any
from rx.core import AnonymousObservable, Observable
from rx.core.typing import Mapper, MapperIndexed, Observer, Disposable, Scheduler

# pylint: disable=redefined-builtin
def _map(mapper: Mapper = None) -> Callable[[Observable], Observable]:
    def map(source: Observable) -> Observable:
        """Partially applied map operator.

        Project each element of an observable sequence into a new form
        by incorporating the element's index.

        Example:
            >>> map(source)

        Args:
            source: The observable source to transform.

        Returns:
            Returns an observable sequence whose elements are the
            result of invoking the transform function on each element
            of the source.
        """
        def subscribe(obv: Observer, scheduler: Scheduler) -> Disposable:
            def on_next(value: Any) -> None:
                try:
                    result = mapper(value)
                except Exception as err:  # pylint: disable=broad-except
                    obv.on_error(err)
                else:
                    obv.on_next(result)

            return source.subscribe_(on_next, obv.on_error, obv.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return map


def _map_indexed(mapper_indexed: MapperIndexed = None) -> Callable[[Observable], Observable]:
    def map_indexed(source: Observable) -> Observable:
        """Partially applied indexed map operator.

        Project each element of an observable sequence into a new form
        by incorporating the element's index.

        Example:
            >>> ret = map_indexed(source)

        Args:
            source: The observable source to transform.

        Returns:
            Returns an observable sequence whose elements are the
            result of invoking the transform function on each element
            of the source.
        """

        def subscribe(obv: Observer, scheduler: Scheduler) -> Disposable:
            count = 0

            def on_next(value: Any) -> None:
                nonlocal count

                try:
                    result = mapper_indexed(value, count)
                except Exception as err:  # pylint: disable=broad-except
                    obv.on_error(err)
                else:
                    count += 1
                    obv.on_next(result)

            return source.subscribe_(on_next, obv.on_error, obv.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return map_indexed
