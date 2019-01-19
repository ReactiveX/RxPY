from typing import Any

from rx.disposables import CompositeDisposable
from .exceptions import DisposedException


def add_ref(xs, r):
    from rx.core import AnonymousObservable

    def subscribe(observer, scheduler=None):
        return CompositeDisposable(r.disposable, xs.subscribe(observer))

    return AnonymousObservable(subscribe)


def check_disposed(this):
    if this.is_disposed:
        raise DisposedException()


def is_future(fut: Any) -> bool:
    return callable(getattr(fut, "add_done_callback", None))


def infinite():
    n = 0
    while True:
        yield n
        n += 1


class TimeInterval(object):

    def __init__(self, value, interval):
        self.value = value
        self.interval = interval


class Timestamp(object):

    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp
