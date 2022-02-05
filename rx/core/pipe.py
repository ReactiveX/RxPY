from functools import reduce
from typing import Any, Callable, TypeVar, overload

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")
_F = TypeVar("_F")
_G = TypeVar("_G")


@overload
def pipe(__op1: Callable[[_A], _B]) -> Callable[[_A], _B]:
    ...


@overload
def pipe(__op1: Callable[[_A], _B], __op2: Callable[[_B], _C]) -> Callable[[_A], _C]:
    ...


@overload
def pipe(
    __op1: Callable[[_A], _B],
    __op2: Callable[[_B], _C],
    __op3: Callable[[_C], _D],
) -> Callable[[_A], _D]:
    ...


@overload
def pipe(
    __op1: Callable[[_A], _B],
    __op2: Callable[[_B], _C],
    __op3: Callable[[_C], _D],
    __op4: Callable[[_D], _E],
) -> Callable[[_A], _E]:
    ...


@overload
def pipe(
    __op1: Callable[[_A], _B],
    __op2: Callable[[_B], _C],
    __op3: Callable[[_C], _D],
    __op4: Callable[[_D], _E],
    __op5: Callable[[_E], _F],
) -> Callable[[_A], _F]:
    ...


@overload
def pipe(
    __op1: Callable[[_A], _B],
    __op2: Callable[[_B], _C],
    __op3: Callable[[_C], _D],
    __op4: Callable[[_D], _E],
    __op5: Callable[[_E], _F],
    __op6: Callable[[_F], _G],
) -> Callable[[_A], _G]:
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
