from typing import Callable, TypeVar

from reactivex import Observable
from reactivex import operators as ops

_T = TypeVar("_T")


def do_while_(
    condition: Callable[[Observable[_T]], bool]
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Repeats source as long as condition holds emulating a do while
    loop.

    Args:
        condition: The condition which determines if the source will be
            repeated.

    Returns:
        An observable sequence which is repeated as long
        as the condition holds.
    """

    def do_while(source: Observable[_T]) -> Observable[_T]:
        return source.pipe(
            ops.concat(
                source.pipe(
                    ops.while_do(condition),
                ),
            )
        )

    return do_while


__all__ = ["do_while_"]
