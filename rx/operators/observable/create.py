from rx.core import AnonymousObservable


def create(subscribe):
    def _subscribe(observer, _=None):
        return subscribe(observer)
    return AnonymousObservable(_subscribe)
