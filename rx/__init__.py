try:
    import asyncio
except ImportError:
    try:
        import trollius as asyncio
    except ImportError:
        asyncio = None

try:
    from threading import RLock as Lock
except ImportError:
    from rx.internal.concurrency import NoLock as Lock

try:
    from asyncio import Future
except ImportError:
    try:
        from trollius import Future
    except ImportError:
        Future = None


# Rx configuration dictionary
config = {
    "Future": Future,
    "Lock": Lock,
    "asyncio": asyncio
}

from .core import Observer, Observable
from .core.anonymousobserver import AnonymousObserver
from .core.anonymousobservable import AnonymousObservable

from . import backpressure
from . import linq
