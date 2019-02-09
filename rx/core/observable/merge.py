
import rx
from rx import operators as ops
from rx.core import Observable


def _merge(*sources: Observable) -> Observable:
    return rx.from_iterable(sources).pipe(ops.merge_all())
