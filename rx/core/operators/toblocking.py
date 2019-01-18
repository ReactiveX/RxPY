from typing import Callable

from rx.core import Observable
from rx.core.observable import BlockingObservable


def _to_blocking() -> Callable[[Observable], BlockingObservable]:
    def to_blocking(source: Observable) -> BlockingObservable:
        return BlockingObservable(source)
    return to_blocking
