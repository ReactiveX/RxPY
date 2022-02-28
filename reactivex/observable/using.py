from typing import Callable, Optional, TypeVar

import reactivex
from reactivex import Observable, abc
from reactivex.disposable import CompositeDisposable, Disposable

_T = TypeVar("_T")


def using_(
    resource_factory: Callable[[], abc.DisposableBase],
    observable_factory: Callable[[abc.DisposableBase], Observable[_T]],
) -> Observable[_T]:
    """Constructs an observable sequence that depends on a resource
    object, whose lifetime is tied to the resulting observable
    sequence's lifetime.

    Example:
        >>> res = reactivex.using(lambda: AsyncSubject(), lambda: s: s)

    Args:
        resource_factory: Factory function to obtain a resource object.
        observable_factory: Factory function to obtain an observable
            sequence that depends on the obtained resource.

    Returns:
        An observable sequence whose lifetime controls the lifetime
        of the dependent resource object.
    """

    def subscribe(
        observer: abc.ObserverBase[_T], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        disp: abc.DisposableBase = Disposable()

        try:
            resource = resource_factory()
            if resource is not None:
                disp = resource

            source = observable_factory(resource)
        except Exception as exception:  # pylint: disable=broad-except
            d = reactivex.throw(exception).subscribe(observer, scheduler=scheduler)
            return CompositeDisposable(d, disp)

        return CompositeDisposable(
            source.subscribe(observer, scheduler=scheduler), disp
        )

    return Observable(subscribe)


__all__ = ["using_"]
