from typing import Callable, Optional
from rx.core import AnonymousObservable
from rx.core import typing


def create(subscribe: Callable[[typing.Observer, Optional[typing.Scheduler]], typing.Disposable]):
    """Create observable from subscribe function."""

    return AnonymousObservable(subscribe)
