from typing import Callable
from rx.core import ObservableBase as Observable


def let(func, *args, **kwargs) -> Callable[[Observable], Observable]:
    """Returns an observable sequence that is the result of invoking the
    mapper on the source sequence, without sharing subscriptions. This
    operator allows for a fluent style of writing queries that use the
    same sequence multiple times.

    Any kwargs given will be passed through to the mapper. This allows
    for a clean syntax when composing with parameterized mappers.

    Args:
        mapper -- Selector function which can use the source
            sequence as many times as needed, without sharing
            subscriptions to the source sequence.

    Returns:
        A function that takes and observable source and return an
        observable sequence that contains the elements of a
        sequence produced by multicasting the source sequence within a
        mapper function.
    """

    def partial(source: Observable) -> Observable:
        return func(source, *args, **kwargs)
    return partial
