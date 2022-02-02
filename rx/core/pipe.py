from functools import reduce
from typing import Any, Callable, TypeVar, overload

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")
D = TypeVar("D")
E = TypeVar("E")
F = TypeVar("F")
G = TypeVar("G")


@overload
def pipe(*operators: Callable[["Observable"], "Observable"]) -> Callable[["Observable"], "Observable"]:  # type: ignore
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
    ...


@overload
def pipe(__op1: Callable[[A], B]) -> Callable[[A], B]:  # pylint: disable=function-redefined
    ...


@overload
def pipe(__op1: Callable[[A], B], __op2: Callable[[B], C]) -> Callable[[A], C]:  # pylint: disable=function-redefined
    ...


@overload
def pipe(
    __op1: Callable[[A], B], __op2: Callable[[B], C], __op3: Callable[[C], D]  # pylint: disable=function-redefined
) -> Callable[[A], D]:
    ...


@overload
def pipe(
    __op1: Callable[[A], B],
    __op2: Callable[[B], C],
    __op3: Callable[[C], D],
    __op4: Callable[[D], E],
) -> Callable[[A], E]:
    ...


@overload
def pipe(
    __op1: Callable[[A], B],
    __op2: Callable[[B], C],
    __op3: Callable[[C], D],
    __op4: Callable[[D], E],
    __op5: Callable[[E], F],
) -> Callable[[A], F]:
    ...


@overload
def pipe(
    __op1: Callable[[A], B],
    __op2: Callable[[B], C],
    __op3: Callable[[C], D],
    __op4: Callable[[D], E],
    __op5: Callable[[E], F],
    __op6: Callable[[F], G],
) -> Callable[[A], G]:
    ...


def pipe(*operators: Callable[[Any], Any]) -> Callable[[Any], Any]:
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

    def compose(source: Any) -> Any:
        return reduce(lambda obs, op: op(obs), operators, source)

    return compose
