import types
from inspect import getargspec, getargvalues 

from rx import AnonymousObservable
from rx.disposables import CompositeDisposable

def add_ref(xs, r):
    def subscribe(observer):
        return CompositeDisposable(r.disposable, xs.subscribe(observer))

    return AnonymousObservable(subscribe)

def adapt_call(func):
    """Adapts func from taking 3 params to only taking 1 or 2 params"""
    
    def func1(arg1, arg2=None, arg3=None):
        return func(arg1)
    def func2(arg1, arg2=None, arg3=None):
        return func(arg1, arg2)

    func_wrapped = func
    argnames, varargs, kwargs = getargspec(func)[:3]
    if not varargs and not kwargs:
        if len(argnames) == 1: 
            func_wrapped = func1
        elif len(argnames) == 2:
            func_wrapped = func2
    
    return func_wrapped

object_disposed = 'Object has been disposed'
def check_disposed(this):
    if this.is_disposed:
        raise Exception(object_disposed)

def is_future(p):
    return callable(getattr(p, "add_done_callback", None))