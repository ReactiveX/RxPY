from typing import Callable, List, TypeVar

from reactivex import Observable
from reactivex import operators as ops
from reactivex.typing import Predicate, PredicateIndexed

_T = TypeVar("_T")


def partition_(
    predicate: Predicate[_T],
) -> Callable[[Observable[_T]], List[Observable[_T]]]:
    def partition(source: Observable[_T]) -> List[Observable[_T]]:
        """The partially applied `partition` operator.

        Returns two observables which partition the observations of the
        source by the given function. The first will trigger
        observations for those values for which the predicate returns
        true. The second will trigger observations for those values
        where the predicate returns false. The predicate is executed
        once for each subscribed observer. Both also propagate all
        error observations arising from the source and each completes
        when the source completes.

        Args:
            source: Source observable to partition.

        Returns:
            A list of observables. The first triggers when the
            predicate returns True, and the second triggers when the
            predicate returns False.
        """

        def not_predicate(x: _T) -> bool:
            return not predicate(x)

        published = source.pipe(
            ops.publish(),
            ops.ref_count(),
        )
        return [
            published.pipe(ops.filter(predicate)),
            published.pipe(ops.filter(not_predicate)),
        ]

    return partition


def partition_indexed_(
    predicate_indexed: PredicateIndexed[_T],
) -> Callable[[Observable[_T]], List[Observable[_T]]]:
    def partition_indexed(source: Observable[_T]) -> List[Observable[_T]]:
        """The partially applied indexed partition operator.

        Returns two observables which partition the observations of the
        source by the given function. The first will trigger
        observations for those values for which the predicate returns
        true. The second will trigger observations for those values
        where the predicate returns false. The predicate is executed
        once for each subscribed observer. Both also propagate all
        error observations arising from the source and each completes
        when the source completes.

        Args:
            source: Source observable to partition.

        Returns:
            A list of observables. The first triggers when the
            predicate returns True, and the second triggers when the
            predicate returns False.
        """

        def not_predicate_indexed(x: _T, i: int) -> bool:
            return not predicate_indexed(x, i)

        published = source.pipe(
            ops.publish(),
            ops.ref_count(),
        )
        return [
            published.pipe(ops.filter_indexed(predicate_indexed)),
            published.pipe(ops.filter_indexed(not_predicate_indexed)),
        ]

    return partition_indexed


__all__ = ["partition_", "partition_indexed_"]
