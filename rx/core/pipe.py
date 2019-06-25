from typing import Callable, Any, TypeVar, overload
from functools import reduce

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')
E = TypeVar('E')
F = TypeVar('F')
G = TypeVar('G')


@overload
def pipe() -> Callable[[A], A]:
    ...  # pylint: disable=pointless-statement


@overload
# pylint: disable=function-redefined
def pipe(op1: Callable[[A], B]
         ) -> Callable[[A], B]:
    ...  # pylint: disable=pointless-statement


@overload
# pylint: disable=function-redefined
def pipe(op1: Callable[[A], B],
         op2: Callable[[B], C]
         ) -> Callable[[A], C]:
    ...  # pylint: disable=pointless-statement


@overload
# pylint: disable=function-redefined
def pipe(op1: Callable[[A], B],
         op2: Callable[[B], C],
         op3: Callable[[C], D]
         ) -> Callable[[A], D]:
    ...  # pylint: disable=pointless-statement


@overload
# pylint: disable=function-redefined
def pipe(op1: Callable[[A], B],
         op2: Callable[[B], C],
         op3: Callable[[C], D],
         op4: Callable[[D], E]
         ) -> Callable[[A], E]:
    ...  # pylint: disable=pointless-statement


@overload
# pylint: disable=function-redefined,too-many-arguments
def pipe(op1: Callable[[A], B],
         op2: Callable[[B], C],
         op3: Callable[[C], D],
         op4: Callable[[D], E],
         op5: Callable[[E], F]
         ) -> Callable[[A], F]:
    ...  # pylint: disable=pointless-statement


@overload
# pylint: disable=function-redefined,too-many-arguments
def pipe(op1: Callable[[A], B],
         op2: Callable[[B], C],
         op3: Callable[[C], D],
         op4: Callable[[D], E],
         op5: Callable[[E], F],
         op6: Callable[[F], G]
         ) -> Callable[[A], G]:
    ...  # pylint: disable=pointless-statement


@overload
# pylint: disable=function-redefined,too-many-arguments
def pipe(*operators: Callable[['Observable'], 'Observable']  # type: ignore
         ) -> Callable[['Observable'], 'Observable']:        # type: ignore

    ...  # pylint: disable=pointless-statement


# pylint: disable=function-redefined
def pipe(*operators: Callable[[Any], Any], **kwargs) -> Callable[[Any], Any]:
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

    Args:
        operators: Sequence of operators.
        **kwargs: Ignore this, only present to satisfy mypy type checker.

    Returns:
        The composed observable.
    """

    def compose(source: Any) -> Any:
        return reduce(lambda obs, op: op(obs), operators, source)
    return compose
