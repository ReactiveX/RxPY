from rx import concat
from rx.core import Observable
from rx.internal import Iterable


def _for_in(values, result_mapper) -> Observable:
    return concat(Iterable.for_each(values, result_mapper))
