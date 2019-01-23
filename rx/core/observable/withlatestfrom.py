from typing import Any, Iterable, Callable, Union, List, cast

from rx import operators as ops
from rx.core import Observable


def _with_latest_from(*args: Union[Observable, Iterable[Observable]]) -> Observable:
    sources: List[Observable] = []

    if isinstance(args[0], Iterable):
        sources += list(args[0])
    else:
        sources += list(cast(Iterable[Observable], args))

    return ops.with_latest_from(sources[1:])(sources[0])
