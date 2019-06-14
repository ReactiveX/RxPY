from typing import Callable, Optional

from rx import throw
from rx.core import Observable, typing
from rx.disposable import CompositeDisposable, Disposable
from rx.internal.utils import subscribe as _subscribe


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

    def subscribe_observer(observer: typing.Observer,
                           scheduler: Optional[typing.Scheduler] = None
                           ) -> typing.Disposable:
        disp = Disposable()

        try:
            resource = resource_factory()
            if resource is not None:
                disp = resource

            source = observable_factory(resource)
        except Exception as exception:  # pylint: disable=broad-except
            d = _subscribe(throw(exception), observer, scheduler=scheduler)
            return CompositeDisposable(d, disp)

        return CompositeDisposable(
            _subscribe(source, observer, scheduler=scheduler),
            disp
        )
    return Observable(subscribe_observer=subscribe_observer)
