from typing import List, Callable

from rx import operators as ops
from rx.core import Observable
from rx.core.typing import Predicate, PredicateIndexed


def _partition(predicate: Predicate) -> Callable[[Observable], List[Observable]]:
    def partition(source: Observable) -> List[Observable]:
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
            source: Source obserable to partition.

        Returns:
            A list of observables. The first triggers when the
            predicate returns True, and the second triggers when the
            predicate returns False.
        """

        published = source.pipe(
            ops.publish(),
            ops.ref_count()
        )
        return [
            published.pipe(ops.filter(predicate)),
            published.pipe(ops.filter(lambda x: not predicate(x)))
        ]
    return partition


def _partition_indexed(predicate_indexed: PredicateIndexed) -> Callable[[Observable], List[Observable]]:
    def partition_indexed(source: Observable) -> List[Observable]:
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

        published = source.pipe(
            ops.publish(),
            ops.ref_count()
        )
        return [
            published.pipe(ops.filter_indexed(predicate_indexed)),
            published.pipe(ops.filter_indexed(predicate_indexed=lambda x, i: not predicate_indexed(x, i)))
        ]
    return partition_indexed
