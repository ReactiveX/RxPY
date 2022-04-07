from functools import reduce
from typing import Any, Callable, TypeVar, overload

_A = TypeVar("_A")
_B = TypeVar("_B")
_C = TypeVar("_C")
_D = TypeVar("_D")
_E = TypeVar("_E")
_F = TypeVar("_F")
_G = TypeVar("_G")
_H = TypeVar("_H")
_T = TypeVar("_T")
_J = TypeVar("_J")


@overload
def compose(__op1: Callable[[_A], _B]) -> Callable[[_A], _B]:
    ...


@overload
def compose(__op1: Callable[[_A], _B], __op2: Callable[[_B], _C]) -> Callable[[_A], _C]:
    ...


@overload
def compose(
    __op1: Callable[[_A], _B],
    __op2: Callable[[_B], _C],
    __op3: Callable[[_C], _D],
) -> Callable[[_A], _D]:
    ...


@overload
def compose(
    __op1: Callable[[_A], _B],
    __op2: Callable[[_B], _C],
    __op3: Callable[[_C], _D],
    __op4: Callable[[_D], _E],
) -> Callable[[_A], _E]:
    ...


@overload
def compose(
    __op1: Callable[[_A], _B],
    __op2: Callable[[_B], _C],
    __op3: Callable[[_C], _D],
    __op4: Callable[[_D], _E],
    __op5: Callable[[_E], _F],
) -> Callable[[_A], _F]:
    ...


@overload
def compose(
    __op1: Callable[[_A], _B],
    __op2: Callable[[_B], _C],
    __op3: Callable[[_C], _D],
    __op4: Callable[[_D], _E],
    __op5: Callable[[_E], _F],
    __op6: Callable[[_F], _G],
) -> Callable[[_A], _G]:
    ...


def compose(*operators: Callable[[Any], Any]) -> Callable[[Any], Any]:
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

    def _compose(source: Any) -> Any:
        return reduce(lambda obs, op: op(obs), operators, source)

    return _compose


@overload
def pipe(__value: _A) -> _A:
    ...


@overload
def pipe(__value: _A, __fn1: Callable[[_A], _B]) -> _B:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
) -> _C:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
) -> _D:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
) -> _E:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
) -> _F:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
) -> _G:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
    __fn7: Callable[[_G], _H],
) -> _H:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
    __fn7: Callable[[_G], _H],
    __fn8: Callable[[_H], _T],
) -> _T:
    ...


@overload
def pipe(
    __value: _A,
    __fn1: Callable[[_A], _B],
    __fn2: Callable[[_B], _C],
    __fn3: Callable[[_C], _D],
    __fn4: Callable[[_D], _E],
    __fn5: Callable[[_E], _F],
    __fn6: Callable[[_F], _G],
    __fn7: Callable[[_G], _H],
    __fn8: Callable[[_H], _T],
    __fn9: Callable[[_T], _J],
) -> _J:
    ...


def pipe(__value: Any, *fns: Callable[[Any], Any]) -> Any:
    """Functional pipe (`|>`)

    Allows the use of function argument on the left side of the
    function.

    Example:
        >>> pipe(x, fn) == __fn(x)  # Same as x |> fn
        >>> pipe(x, fn, gn) == gn(fn(x))  # Same as x |> fn |> gn
        ...
    """

    return compose(*fns)(__value)


__all__ = ["pipe", "compose"]
