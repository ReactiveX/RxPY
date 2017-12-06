from rx.core import AnonymousObservable


def create(subscribe):
    return AnonymousObservable(subscribe)
