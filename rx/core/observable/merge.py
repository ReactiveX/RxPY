from typing import Iterable, Union

import rx
from rx import operators as ops
from rx.core import Observable



def _merge(*args: Union[Observable, Iterable[Observable]]) -> Observable:
    sources = args[:]

    if isinstance(sources[0], Iterable):
        sources = sources[0]

    return rx.from_iterable(sources).pipe(ops.merge_all())
