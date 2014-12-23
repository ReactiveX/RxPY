from inspect import getargspec

from rx import AnonymousObservable
from rx.disposables import CompositeDisposable

from .exceptions import DisposedException

def add_ref(xs, r):
    def subscribe(observer):
        return CompositeDisposable(r.disposable, xs.subscribe(observer))

    return AnonymousObservable(subscribe)

def adapt_call(func):
    """Adapts func from taking 3 params to only taking 1 or 2 params"""
    
    def func1(arg1, *_):
        return func(arg1)
    def func2(arg1, arg2=None, *_):
        return func(arg1, arg2)

    func_wrapped = func
    argnames, varargs, kwargs = getargspec(func)[:3]
    if not varargs and not kwargs:
        if len(argnames) == 1: 
            func_wrapped = func1
        elif len(argnames) == 2:
            func_wrapped = func2
    
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
