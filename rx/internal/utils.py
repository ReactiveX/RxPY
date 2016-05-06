from rx import AnonymousObservable
from rx.disposables import CompositeDisposable

from .exceptions import DisposedException


def add_ref(xs, r):
    def subscribe(observer):
        return CompositeDisposable(r.disposable, xs.subscribe(observer))

    return AnonymousObservable(subscribe)


def adapt_call(func):
    """Adapt called func.

    Adapt call from taking n params to only taking 1 or 2 params
    """
    cached = [None]

    def func1(arg1, *_):
        return func(arg1)

    def func2(arg1, arg2=None, *_):
        return func(arg1, arg2)

    def func_wrapped(*args, **kw):
        if cached[0]:
            return cached[0](*args, **kw)

        for fn in (func1, func2):
            try:
                ret = fn(*args, **kw)
            except TypeError:
                continue
            else:
                cached[0] = fn
            return ret

        # Error if we get here. Just call original function to generate a
        # meaningful error message
        return func(*args, **kw)
    return func_wrapped


def check_disposed(this):
    if this.is_disposed:
        raise DisposedException()


def is_future(p):
    return callable(getattr(p, "add_done_callback", None))


class TimeInterval(object):

    def __init__(self, value, interval):
        self.value = value
        self.interval = interval


class Timestamp(object):

    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp
