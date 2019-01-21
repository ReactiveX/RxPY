from typing import Iterable, Union

import rx
from rx import operators as ops
from rx.core import Observable



def _merge(*args: Union[Observable, Iterable[Observable]]) -> Observable:
    """Merges all the observable sequences into a single observable
    sequence.

    1 - merged = rx.merge(xs, ys, zs)
    2 - merged = rx.merge([xs, ys, zs])

    Returns:
        The observable sequence that merges the elements of the
        observable sequences.
    """

    sources = args[:]

    if isinstance(sources[0], Iterable):
        sources = sources[0]

    return rx.from_iterable(sources).pipe(ops.merge_all())
