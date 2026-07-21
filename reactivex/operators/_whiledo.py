import itertools
from collections.abc import Callable
from typing import TypeVar, Union

import reactivex
from reactivex import Observable
from reactivex.internal.utils import infinite, is_future
from reactivex.typing import AnyFuture, Predicate

_T = TypeVar("_T")


def while_do_(
    condition: Predicate[Observable[_T]],
) -> Callable[[Observable[_T]], Observable[_T]]:
    def while_do(source: Union[Observable[_T], "AnyFuture[_T]"]) -> Observable[_T]:
        """Repeats source as long as condition holds emulating a while
        loop.

        Args:
            source: The observable sequence that will be run if the
                condition function returns true.

        Returns:
            An observable sequence which is repeated as long as the
            condition holds.
        """
        if is_future(source):
            obs = reactivex.from_future(source)
        else:
            obs = source
        it = itertools.takewhile(condition, (obs for _ in infinite()))
        return reactivex.concat_with_iterable(it)

    return while_do


__all__ = ["while_do_"]
