from typing import Callable, Optional, TypeVar, cast

from reactivex import Observable, abc, compose
from reactivex import operators as ops
from reactivex import typing
from reactivex.internal.basic import identity
from reactivex.internal.utils import infinite
from reactivex.typing import Mapper, MapperIndexed

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def map_(
    mapper: Optional[Mapper[_T1, _T2]] = None,
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    _mapper = mapper or cast(Mapper[_T1, _T2], identity)

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

        def subscribe(
            obv: abc.ObserverBase[_T2], scheduler: Optional[abc.SchedulerBase] = None
        ) -> abc.DisposableBase:
            def on_next(value: _T1) -> None:
                try:
                    result = _mapper(value)
                except Exception as err:  # pylint: disable=broad-except
                    obv.on_error(err)
                else:
                    obv.on_next(result)

            return source.subscribe(
                on_next, obv.on_error, obv.on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return map


def map_indexed_(
    mapper_indexed: Optional[MapperIndexed[_T1, _T2]] = None,
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    def _identity(value: _T1, _: int) -> _T2:
        return cast(_T2, value)

    _mapper_indexed = mapper_indexed or cast(typing.MapperIndexed[_T1, _T2], _identity)

    return compose(
        ops.zip_with_iterable(infinite()),
        ops.starmap_indexed(_mapper_indexed),  # type: ignore
    )


__all__ = ["map_", "map_indexed_"]
