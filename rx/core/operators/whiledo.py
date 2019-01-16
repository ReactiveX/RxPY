from typing import Callable

import rx
from rx.core import Observable

from rx.internal.iterable import Iterable
from rx.internal.utils import is_future


def _while_do(condition) -> Callable[[Observable], Observable]:
    def while_do(source: Observable) -> Observable:
        """Repeats source as long as condition holds emulating a while
        loop.

        Args:
            source: The observable sequence that will be run if the
                condition function returns true.

        Returns:
            An observable sequence which is repeated as long as the
            condition holds.
        """
        source = rx.from_future(source) if is_future(source) else source
        return rx.concat(Iterable.while_do(condition, source))
    return while_do
