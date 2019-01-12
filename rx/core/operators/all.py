from typing import Callable

from rx import operators as ops
from rx.core import Observable, pipe
from rx.core.typing import Predicate


def _all(predicate: Predicate) -> Callable[[Observable], Observable]:

    filtering = ops.filter(lambda v: not predicate(v))
    mapping = ops.map(lambda b: not b)
    some = ops.some()

    return pipe(
        filtering,
        some,
        mapping
    )
