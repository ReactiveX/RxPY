import collections
from typing import Callable, Optional

from rx import from_, from_future, operators as ops
from rx.core import Observable
from rx.core.typing import Mapper, MapperIndexed
from rx.internal.utils import is_future


def _flat_map_internal(source, mapper=None, mapper_indexed=None):
    def projection(x, i):
        mapper_result = mapper(x) if mapper else mapper_indexed(x, i)
        if is_future(mapper_result):
            result = from_future(mapper_result)
        elif isinstance(mapper_result, collections.abc.Iterable):
            result = from_(mapper_result)
        else:
            result = mapper_result
        return result

    return source.pipe(
        ops.map_indexed(projection),
        ops.merge_all()
    )


def _flat_map(mapper: Optional[Mapper] = None) -> Callable[[Observable], Observable]:
    def flat_map(source: Observable) -> Observable:
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


def _flat_map_indexed(mapper_indexed: Optional[MapperIndexed] = None) -> Callable[[Observable], Observable]:
    def flat_map_indexed(source: Observable) -> Observable:
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


def _flat_map_latest(mapper: Mapper) -> Callable[[Observable], Observable]:
    def flat_map_latest(source: Observable) -> Observable:
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
            ops.switch_latest()
        )
    return flat_map_latest
