from rx import throw
from rx.core import Observable, AnonymousObservable, Disposable
from rx.disposables import CompositeDisposable


def _using(resource_factory, observable_factory) -> Observable:
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
        disposable = Disposable.empty()
        try:
            resource = resource_factory()
            if resource:
                disposable = resource

            source = observable_factory(resource)
        except Exception as exception:
            d = throw(exception).subscribe(observer, scheduler)
            return CompositeDisposable(d, disposable)

        return CompositeDisposable(source.subscribe(observer, scheduler), disposable)
    return AnonymousObservable(subscribe)
