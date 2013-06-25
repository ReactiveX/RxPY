from rx import AnonymousObservable
from rx.disposables import CompositeDisposable

def add_ref(xs, r):
    def subscribe(observer):
        return CompositeDisposable(r.disposable, xs.subscribe(observer))

    return AnonymousObservable(subscribe)