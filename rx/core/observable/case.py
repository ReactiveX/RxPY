from typing import Optional, Mapping, Callable, Hashable

from rx import empty, defer, from_future
from rx.core import Observable
from rx.internal.utils import is_future


def _case(mapper: Callable[[], Hashable],
          sources: Mapping[Hashable, Observable],
          default_source: Optional[Observable] = None
          ) -> Observable:

    default_source = default_source or empty()

    def factory(_) -> Observable:
        try:
            result = sources[mapper()]
        except KeyError:
            result = default_source

        result = from_future(result) if is_future(result) else result

        return result
    return defer(factory)
