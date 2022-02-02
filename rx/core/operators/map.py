from typing import Any, Callable, Optional, TypeVar

from rx import operators as ops
from rx.core import Observable, abc, pipe
from rx.core.typing import Mapper, MapperIndexed
from rx.internal.basic import identity
from rx.internal.utils import infinite

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")

# pylint: disable=redefined-builtin
def _map(mapper: Optional[Mapper[_T1, _T2]] = None) -> Callable[[Observable[_T1]], Observable[_T2]]:

    _mapper = mapper or identity

    def map(source: Observable[_T1]) -> Observable[_T2]:
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

        def subscribe(obv: abc.ObserverBase[_T2], scheduler: Optional[abc.SchedulerBase] = None) -> abc.DisposableBase:
            def on_next(value: Any) -> None:
                try:
                    result = _mapper(value)
                except Exception as err:  # pylint: disable=broad-except
                    obv.on_error(err)
                else:
                    obv.on_next(result)

            return source.subscribe_(on_next, obv.on_error, obv.on_completed, scheduler)

        return Observable(subscribe)

    return map


def _map_indexed(
    mapper_indexed: Optional[MapperIndexed[_T1, _T2]] = None
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    def _identity(value: Any, _: int) -> Any:
        return value

    _mapper_indexed = mapper_indexed or _identity

    return pipe(ops.zip_with_iterable(infinite()), ops.starmap_indexed(_mapper_indexed))


__all__ = ["_map", "_map_indexed"]
