try:
    import asyncio
except ImportError:
    try:
        import trollius as asyncio
    except ImportError:
        asyncio = None

try:
    from threading import Lock
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

from .observable import Observable
from .anonymousobservable import AnonymousObservable
from .observer import Observer

from . import checkedobserver
from . import linq
from . import backpressure


