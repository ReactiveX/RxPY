from threading import Thread
from typing import Optional, Tuple

from rx.core.typing import StartableTarget


def default_thread_factory(target: StartableTarget, args: Optional[Tuple] = None) -> Thread:
    return Thread(target=target, args=args or (), daemon=True)


def synchronized(lock):
    """A decorator for synchronizing access to a given function."""

    def wrapper(fn):
        def inner(*args, **kw):
            with lock:
                return fn(*args, **kw)
        return inner
    return wrapper
