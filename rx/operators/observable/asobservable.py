from rx.core import Observable, AnonymousObservable


def as_observable(source) -> Observable:
    """Hides the identity of an observable sequence.

    :returns: An observable sequence that hides the identity of the source
        sequence.
    :rtype: Observable
    """

    def subscribe(observer):
        nonlocal source
        return source.subscribe(observer)

    return AnonymousObservable(subscribe)
