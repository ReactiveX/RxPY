from rx.internal.concurrency import NoLock as Lock

Future = None

# Rx configuration dictionary
config = {
    "Future" : Future,
    "Lock" : Lock
}

from .observable import Observable
from .anonymousobservable import AnonymousObservable
from .observer import Observer

from . import checkedobserver
from . import linq
from . import backpressure


