try:
    import asyncio
except ImportError:
    asyncio = None

try:
    from asyncio import Future
except ImportError:
    Future = None

try:
    import threading
except ImportError:
    import rx.internal.concurrency as threading

# Rx configuration dictionary
config = {
    "concurrency": threading,
    "Future": Future,
    "Lock": threading.RLock,  # Deprecated
    "asyncio": asyncio
}

from .core import Observer, Observable
from .core.anonymousobserver import AnonymousObserver
from .core.anonymousobservable import AnonymousObservable

from . import backpressure
from . import operators
