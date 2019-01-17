from typing import Callable, Any

from rx import operators as ops
from rx.core import Observable


def _do_while(condition: Callable[[Any], bool]) -> Callable[[Observable], Observable]:
    """Repeats source as long as condition holds emulating a do while
    loop.

    Args:
        condition: The condition which determines if the source will be
            repeated.

    Returns:
        An observable sequence which is repeated as long
        as the condition holds.
    """

    def do_while(source: Observable) -> Observable:
        return source.pipe(ops.concat(source.pipe(ops.while_do(condition))))
    return do_while
