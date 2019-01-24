from typing import Callable
from functools import reduce
from .observable import ObservableBase as Observable


def pipe(*operators: Callable[[Observable], Observable]) -> Callable[[Observable], Observable]:
    """Compose multiple operators left to right.

    Composes zero or more operators into a functional composition. The
    operators are composed to left to right. A composition of zero
    operators gives back the source.

    Examples:
        >>> pipe()(source) == source
        >>> pipe(f)(source) == f(source)
        >>> pipe(f, g)(source) == g(f(source))
        >>> pipe(f, g, h)(source) == h(g(f(source)))
        ...

    Returns:
        The composed observable.
    """

    def compose(source: Observable) -> Observable:
        return reduce(lambda obs, op: op(obs), operators, source)
    return compose
