from typing import Optional

from rx.disposable import Disposable
from rx.core import Observable, typing


def _never() -> Observable:
    """Returns a non-terminating observable sequence, which can be used
    to denote an infinite duration (e.g. when using reactive joins).

    Returns:
        An observable sequence whose observers will never get called.
    """

    def subscribe(observer: typing.Observer, scheduler: Optional[typing.Scheduler] = None) -> typing.Disposable:
        return Disposable()

    return Observable(subscribe)
