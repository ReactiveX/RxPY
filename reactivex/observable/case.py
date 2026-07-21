from collections.abc import Callable, Mapping
from typing import TypeVar, Union

from reactivex import Observable, abc, defer, empty, from_future
from reactivex.internal import is_future
from reactivex.typing import AnyFuture

_Key = TypeVar("_Key")
_T = TypeVar("_T")


def case_(
    mapper: Callable[[], _Key],
    sources: Mapping[_Key, Observable[_T]],
    default_source: Union[Observable[_T], "AnyFuture[_T]"] | None = None,
) -> Observable[_T]:
    default_source_: Observable[_T] | AnyFuture[_T] = default_source or empty()

    def factory(_: abc.SchedulerBase) -> Observable[_T]:
        try:
            result: Observable[_T] | AnyFuture[_T] = sources[mapper()]
        except KeyError:
            result = default_source_

        if is_future(result):
            result_: Observable[_T] = from_future(result)
        else:
            result_ = result

        return result_

    return defer(factory)


__all__ = ["case_"]
