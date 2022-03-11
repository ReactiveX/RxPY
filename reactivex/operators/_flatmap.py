from asyncio import Future
from typing import Any, Callable, Optional, TypeVar, Union, cast

from reactivex import Observable, from_, from_future
from reactivex import operators as ops
from reactivex.internal.basic import identity
from reactivex.typing import Mapper, MapperIndexed

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def _flat_map_internal(
    source: Observable[_T1],
    mapper: Optional[Mapper[_T1, Any]] = None,
    mapper_indexed: Optional[MapperIndexed[_T1, Any]] = None,
) -> Observable[Any]:
    def projection(x: _T1, i: int) -> Observable[Any]:
        mapper_result: Any = (
            mapper(x)
            if mapper
            else mapper_indexed(x, i)
            if mapper_indexed
            else identity
        )
        if isinstance(mapper_result, Future):
            result: Observable[Any] = from_future(cast("Future[Any]", mapper_result))
        elif isinstance(mapper_result, Observable):
            result = mapper_result
        else:
            result = from_(mapper_result)
        return result

    return source.pipe(
        ops.map_indexed(projection),
        ops.merge_all(),
    )


def flat_map_(
    mapper: Optional[Mapper[_T1, Observable[_T2]]] = None
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    def flat_map(source: Observable[_T1]) -> Observable[_T2]:
        """One of the Following:
        Projects each element of an observable sequence to an observable
        sequence and merges the resulting observable sequences into one
        observable sequence.

        Example:
            >>> flat_map(source)

        Args:
            source: Source observable to flat map.

        Returns:
            An operator function that takes a source observable and returns
            an observable sequence whose elements are the result of invoking
            the one-to-many transform function on each element of the
            input sequence .
        """

        if callable(mapper):
            ret = _flat_map_internal(source, mapper=mapper)
        else:
            ret = _flat_map_internal(source, mapper=lambda _: mapper)

        return ret

    return flat_map


def flat_map_indexed_(
    mapper_indexed: Optional[Any] = None,
) -> Callable[[Observable[Any]], Observable[Any]]:
    def flat_map_indexed(source: Observable[Any]) -> Observable[Any]:
        """One of the Following:
        Projects each element of an observable sequence to an observable
        sequence and merges the resulting observable sequences into one
        observable sequence.

        Example:
            >>> flat_map_indexed(source)

        Args:
            source: Source observable to flat map.

        Returns:
            An observable sequence whose elements are the result of invoking
            the one-to-many transform function on each element of the input
            sequence.
        """

        if callable(mapper_indexed):
            ret = _flat_map_internal(source, mapper_indexed=mapper_indexed)
        else:
            ret = _flat_map_internal(source, mapper=lambda _: mapper_indexed)
        return ret

    return flat_map_indexed


def flat_map_latest_(
    mapper: Mapper[_T1, Union[Observable[_T2], "Future[_T2]"]]
) -> Callable[[Observable[_T1]], Observable[_T2]]:
    def flat_map_latest(source: Observable[_T1]) -> Observable[_T2]:
        """Projects each element of an observable sequence into a new
        sequence of observable sequences by incorporating the element's
        index and then transforms an observable sequence of observable
        sequences into an observable sequence producing values only
        from the most recent observable sequence.

        Args:
            source: Source observable to flat map latest.

        Returns:
            An observable sequence whose elements are the result of
            invoking the transform function on each element of source
            producing an observable of Observable sequences and that at
            any point in time produces the elements of the most recent
            inner observable sequence that has been received.
        """

        return source.pipe(
            ops.map(mapper),
            ops.switch_latest(),
        )

    return flat_map_latest


__all__ = ["flat_map_", "flat_map_latest_", "flat_map_indexed_"]
