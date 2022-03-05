from typing import Any, Optional

from reactivex import Observable, abc
from reactivex.disposable import Disposable


def never_() -> Observable[Any]:
    """Returns a non-terminating observable sequence, which can be used
    to denote an infinite duration (e.g. when using reactive joins).

    Returns:
        An observable sequence whose observers will never get called.
    """

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        return Disposable()

    return Observable(subscribe)


__all__ = ["never_"]
