from rx import concat
from rx.core import Observable


def _for_in(values, result_mapper) -> Observable:
    return concat(result_mapper(value) for value in values)
