from rx.core import Observable, AnonymousObservable


def as_observable(source) -> Observable:
    """Hides the identity of an observable sequence.

    Returns an observable sequence that hides the identity of the source
        sequence.
    """

    def subscribe(observer, scheduler=None):
        return source.subscribe(observer, scheduler)

    return AnonymousObservable(subscribe)
