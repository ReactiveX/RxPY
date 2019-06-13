from typing import Callable, Any, Optional

from rx.internal.basic import identity
from rx.internal.utils import infinite

from rx import operators as ops
from rx.core import Observable, pipe, typing
from rx.core.typing import Mapper, MapperIndexed, Observer, Disposable, Scheduler


# pylint: disable=redefined-builtin
def _map(mapper: Optional[Mapper] = None) -> Callable[[Observable], Observable]:

    _mapper = mapper or identity

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

        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            def on_next(value: Any) -> None:
                try:
                    result = _mapper(value)
                except Exception as err:  # pylint: disable=broad-except
                    observer.on_error(err)
                else:
                    observer.on_next(result)

            return source.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler=scheduler
            )
        return Observable(subscribe_observer=subscribe_observer)
    return map


def _map_indexed(mapper_indexed: Optional[MapperIndexed] = None) -> Callable[[Observable], Observable]:

    def _identity(value: Any, _: int) -> Any:
        return value

    _mapper_indexed = mapper_indexed or _identity

    return pipe(
        ops.zip_with_iterable(infinite()),
        ops.starmap_indexed(_mapper_indexed)
    )
