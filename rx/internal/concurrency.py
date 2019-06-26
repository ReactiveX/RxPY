from threading import Thread

from rx.core.typing import StartableTarget


def default_thread_factory(target: StartableTarget) -> Thread:
    return Thread(target=target, daemon=True)


def synchronized(lock):
    """A decorator for synchronizing access to a given function."""

    def wrapper(fn):
        def inner(*args, **kw):
            with lock:
                return fn(*args, **kw)
        return inner
    return wrapper
