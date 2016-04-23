import sys

if sys.version_info >= (3, 0):
    from .py3.observer import Observer
    from .py3.observable import Observable
else:
    from .py2.observer import Observer
    from .py2.observable import Observable
