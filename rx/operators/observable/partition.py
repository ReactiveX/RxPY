from typing import List, Callable
from rx.core import ObservableBase
from rx.core.typing import Predicate, PredicateIndexed


def partition(predicate: Predicate = None) -> Callable[[ObservableBase], List[ObservableBase]]:
    """Returns two observables which partition the observations of the
    source by the given function. The first will trigger observations for
    those values for which the predicate returns true. The second will
    trigger observations for those values where the predicate returns false.
    The predicate is executed once for each subscribed observer. Both also
    propagate all error observations arising from the source and each
    completes when the source completes.

    Keyword arguments:
    predicate -- The function to determine which output Observable will
        trigger a particular observation.

    Returns a list of observables. The first triggers when the predicate
    returns True, and the second triggers when the predicate returns False.
    """

    def partial(source: ObservableBase) -> List[ObservableBase]:
        published = source.publish().ref_count()
        return [
            published.filter(predicate),
            published.filter(lambda x: not predicate(x))
        ]
    return partial


def partitioni(predicate_indexed: PredicateIndexed = None) -> Callable[[ObservableBase], List[ObservableBase]]:
    """Returns two observables which partition the observations of the
    source by the given function. The first will trigger observations for
    those values for which the predicate returns true. The second will
    trigger observations for those values where the predicate returns false.
    The predicate is executed once for each subscribed observer. Both also
    propagate all error observations arising from the source and each
    completes when the source completes.

    Keyword arguments:
    predicate -- The function to determine which output Observable will
        trigger a particular observation.

    Returns a list of observables. The first triggers when the predicate
    returns True, and the second triggers when the predicate returns False.
    """

    def partial(source: ObservableBase) -> List[ObservableBase]:
        published = source.publish().ref_count()
        return [
            published.filteri(predicate_indexed),
            published.filteri(predicate_indexed=lambda x,
                              i: not predicate_indexed(x, i))
        ]
    return partial
