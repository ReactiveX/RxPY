from functools import update_wrapper
from types import FunctionType
from typing import TYPE_CHECKING, Any, Callable, Iterable, Optional, TypeVar, cast

from typing_extensions import ParamSpec

from reactivex import abc
from reactivex.disposable import CompositeDisposable
from reactivex.disposable.refcountdisposable import RefCountDisposable

if TYPE_CHECKING:
    from reactivex import Observable

_T = TypeVar("_T")
_P = ParamSpec("_P")


def add_ref(xs: "Observable[_T]", r: RefCountDisposable) -> "Observable[_T]":
    from reactivex import Observable

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        return CompositeDisposable(r.disposable, xs.subscribe(observer))

    return Observable(subscribe)


def infinite() -> Iterable[int]:
    n = 0
    while True:
        yield n
        n += 1


def alias(name: str, doc: str, fun: Callable[_P, _T]) -> Callable[_P, _T]:
    # Adapted from
    # https://stackoverflow.com/questions/13503079/how-to-create-a-copy-of-a-python-function#
    # See also help(type(lambda: 0))
    _fun = cast(FunctionType, fun)
    args = (_fun.__code__, _fun.__globals__)
    kwargs = {"name": name, "argdefs": _fun.__defaults__, "closure": _fun.__closure__}
    alias_ = FunctionType(*args, **kwargs)  # type: ignore
    alias_ = update_wrapper(alias_, _fun)  # type: ignore
    alias_.__kwdefaults__ = _fun.__kwdefaults__  # type: ignore
    alias_.__doc__ = doc
    alias_.__annotations__ = _fun.__annotations__
    return cast(Callable[_P, _T], alias_)


class NotSet:
    """Sentinel value."""

    def __eq__(self, other: Any) -> bool:
        return self is other

    def __repr__(self) -> str:
        return "NotSet"


__all__ = ["add_ref", "infinite", "alias", "NotSet"]
