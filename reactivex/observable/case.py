from asyncio import Future
from typing import Callable, Mapping, Optional, TypeVar, Union

from reactivex import Observable, abc, defer, empty, from_future

_Key = TypeVar("_Key")
_T = TypeVar("_T")


def case_(
    mapper: Callable[[], _Key],
    sources: Mapping[_Key, Observable[_T]],
    default_source: Optional[Union[Observable[_T], "Future[_T]"]] = None,
) -> Observable[_T]:

    default_source_: Union[Observable[_T], "Future[_T]"] = default_source or empty()

    def factory(_: abc.SchedulerBase) -> Observable[_T]:
        try:
            result: Union[Observable[_T], "Future[_T]"] = sources[mapper()]
        except KeyError:
            result = default_source_

        if isinstance(result, Future):

            result_: Observable[_T] = from_future(result)
        else:
            result_ = result

        return result_

    return defer(factory)


__all__ = ["case_"]
