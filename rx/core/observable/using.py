from typing import Callable

import rx
from rx.core import Observable
from rx.core import typing
from rx.disposable import CompositeDisposable, Disposable


def _using(resource_factory: Callable[[], typing.Disposable],
           observable_factory: Callable[[typing.Disposable], Observable]
           ) -> Observable:
    """Constructs an observable sequence that depends on a resource
    object, whose lifetime is tied to the resulting observable
    sequence's lifetime.

    Example:
        >>> res = rx.using(lambda: AsyncSubject(), lambda: s: s)

    Args:
        resource_factory: Factory function to obtain a resource object.
        observable_factory: Factory function to obtain an observable
            sequence that depends on the obtained resource.

    Returns:
        An observable sequence whose lifetime controls the lifetime
        of the dependent resource object.
    """

    def subscribe(observer, scheduler=None):
        disp = Disposable()

        try:
            resource = resource_factory()
            if resource is not None:
                disp = resource

            source = observable_factory(resource)
        except Exception as exception:  # pylint: disable=broad-except
            d = rx.throw(exception).subscribe(observer, scheduler=scheduler)
            return CompositeDisposable(d, disp)

        return CompositeDisposable(source.subscribe(observer, scheduler=scheduler), disp)
    return Observable(subscribe)
