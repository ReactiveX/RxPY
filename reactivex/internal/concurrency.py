from threading import RLock, Thread
from typing import Any, Callable

from reactivex.typing import StartableTarget


def default_thread_factory(target: StartableTarget) -> Thread:
    return Thread(target=target, daemon=True)


def synchronized(lock: RLock) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """A decorator for synchronizing access to a given function."""

    def wrapper(fn: Callable[..., Any]) -> Callable[..., Any]:
        def inner(*args: Any, **kw: Any) -> Any:
            with lock:
                return fn(*args, **kw)

        return inner

    return wrapper
