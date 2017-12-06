from rx.core import Observable, AnonymousObservable, Disposable


def never() -> Observable:
    """Returns a non-terminating observable sequence, which can be used to
    denote an infinite duration (e.g. when using reactive joins).

    Returns an observable sequence whose observers will never get called.
    """

    def subscribe(_):
        return Disposable.empty()

    return AnonymousObservable(subscribe)
