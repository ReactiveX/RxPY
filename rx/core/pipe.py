from typing import Callable
from functools import reduce
from .observablebase import ObservableBase


def pipe(*operators: Callable[[ObservableBase], ObservableBase]) -> ObservableBase:
    """Compose multiple operators left to right.

    Composes zero or more operators into a functional composition. The
    operators are composed to right. A composition of zero
    operators gives back the source.

    Examples:
        pipe()(source) == source
        pipe(f)(source) == f(source)
        pipe(f, g)(source) == g(f(source))
        pipe(f, g, h)(source) == h(g(f(source)))
    ...

    Returns the composed observable.
    """

    def compose(source: ObservableBase) -> Callable[[ObservableBase], ObservableBase]:
        ret = reduce(lambda ops, op: lambda f: f(ops(op)),
                     operators,
                     lambda op: op(source))
        return ret(lambda x: x)
    return compose
