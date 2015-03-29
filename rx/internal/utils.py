import types
try:
    from inspect import getargspec
except ImportError:
    getargspec = None

from rx import AnonymousObservable
from rx.disposables import CompositeDisposable

from .exceptions import DisposedException


def add_ref(xs, r):
    def subscribe(observer):
        return CompositeDisposable(r.disposable, xs.subscribe(observer))

    return AnonymousObservable(subscribe)


def adapt_call_1(func):
    """Adapts func from taking 3 params to only taking 1 or 2 params"""

    func_types = (
        types.FunctionType,
        types.MethodType,
    )
    if hasattr(func, '__call__') and not isinstance(func, func_types):
        func = func.__call__

    def func1(arg1, *_):
        return func(arg1)

    def func2(arg1, arg2=None, *_):
        return func(arg1, arg2)

    func_wrapped = func
    argnames, varargs, kwargs = getargspec(func)[:3]

    if not varargs and not kwargs:
        num_args = len(argnames)
        if hasattr(func, '__self__'):
            num_args -= 1
        if num_args == 1:
            func_wrapped = func1
        elif num_args == 2:
            func_wrapped = func2

    return func_wrapped


def adapt_call_2(func):
    """Adapts func from taking n params to only taking 1 or 2 params"""

    def func1(arg1, *_):
        return func(arg1)

    def func2(arg1, arg2=None, *_):
        return func(arg1, arg2)

    def func_wrapped(*args, **kw):
        for fn in (func1, func2):
            try:
                return fn(*args, **kw)
            except TypeError:
                pass
        # Error if we get here. Just call original function to generate a
        # meaningful error message
        return func(*args, **kw)
    return func_wrapped

# if we have getargspec we use adapt_call_1, since it's faster
if getargspec is not None:
    adapt_call = adapt_call_1
else:
    adapt_call = adapt_call_2


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
