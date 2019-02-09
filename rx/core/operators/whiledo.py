from typing import Callable, Any
import itertools

import rx
from rx.core import Observable

from rx.internal.utils import is_future, infinite


def _while_do(condition: Callable[[Any], bool]) -> Callable[[Observable], Observable]:
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
        return rx.concat_with_iterable(itertools.takewhile(condition, (source for x in infinite())))
    return while_do
