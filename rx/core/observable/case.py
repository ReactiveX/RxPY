from typing import Callable, Mapping, Optional, TypeVar, Union

from rx import defer, empty, from_future
from rx.core import Observable, typing, abc

_Key = TypeVar("_Key")
_T = TypeVar("_T")


def _case(
    mapper: Callable[[], _Key],
    sources: Mapping[_Key, Observable[_T]],
    default_source: Optional[Union[Observable[_T], typing.Future]] = None,
) -> Observable[_T]:

    default_source_: Union[Observable[_T], typing.Future] = default_source or empty()

    def factory(_: abc.SchedulerBase) -> Observable[_T]:
        try:
            result: Union[Observable[_T], typing.Future] = sources[mapper()]
        except KeyError:
            result = default_source_

        if isinstance(result, typing.Future):

            result_: Observable[_T] = from_future(result)
        else:
            result_ = result

        return result_

    return defer(factory)


__all__ = ["_case"]
