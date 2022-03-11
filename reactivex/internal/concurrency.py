from threading import RLock, Thread
from typing import Any, Callable, TypeVar

from typing_extensions import ParamSpec

from reactivex.typing import StartableTarget

_T = TypeVar("_T")
_P = ParamSpec("_P")


def default_thread_factory(target: StartableTarget) -> Thread:
    return Thread(target=target, daemon=True)


def synchronized(lock: RLock) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    """A decorator for synchronizing access to a given function."""

    def wrapper(fn: Callable[_P, _T]) -> Callable[_P, _T]:
        def inner(*args: _P.args, **kw: _P.kwargs) -> Any:
            with lock:
                return fn(*args, **kw)

        return inner

    return wrapper
