from typing import Iterable, Callable, Union, cast

import rx
from rx.core import Observable


def _concat(*args: Union[Observable, Iterable[Observable]]) -> Callable[[Observable], Observable]:
    if args and isinstance(args[0], Iterable):
        sources = iter(args[0])
    else:
        sources = iter(cast(Iterable, args))

    def concat(source: Observable) -> Observable:
        return rx.concat(source, *sources)
    return concat
