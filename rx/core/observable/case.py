from asyncio import Future
from typing import Any, Callable, Mapping, Optional, TypeVar, Union

from rx import defer, empty, from_future
from rx.core import Observable
from rx.internal.utils import is_future

_Key = TypeVar("_Key")
_T = TypeVar("_T")


def _case(
    mapper: Callable[[], _Key],
    sources: Mapping[_Key, Observable[_T]],
    default_source: Optional[Union[Observable[_T], Future]] = None,
) -> Observable[_T]:

    default_source: Union[Observable[_T], Future] = default_source or empty()

    def factory(_) -> Observable[_T]:
        try:
            result = sources[mapper()]
        except KeyError:
            result = default_source

        result: Observable[_T] = from_future(result) if is_future(result) else result

        return result

    return defer(factory)


__all__ = ["_case"]
