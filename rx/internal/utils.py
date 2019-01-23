from typing import Any, Iterable

from rx.disposable import CompositeDisposable


def add_ref(xs, r):
    from rx.core import AnonymousObservable

    def subscribe(observer, scheduler=None):
        return CompositeDisposable(r.disposable, xs.subscribe(observer))

    return AnonymousObservable(subscribe)


def is_future(fut: Any) -> bool:
    return callable(getattr(fut, "add_done_callback", None))


def infinite() -> Iterable[int]:
    n = 0
    while True:
        yield n
        n += 1


class NotSet:
    def __repr__(self):
        return 'NotSet'

