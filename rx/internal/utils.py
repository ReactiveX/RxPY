from rx import AnonymousObservable
from rx.disposables import CompositeDisposable

from .exceptions import DisposedException

def add_ref(xs, r):
    def subscribe(observer):
        return CompositeDisposable(r.disposable, xs.subscribe(observer))

    return AnonymousObservable(subscribe)

def check_disposed(this):
    if this.is_disposed:
        raise DisposedException()

def is_future(p):
    return callable(getattr(p, "add_done_callback", None))