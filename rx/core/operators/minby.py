from typing import Callable, Optional

from rx.core import Observable
from rx.core.typing import Mapper, SubComparer
from rx.internal.basic import default_sub_comparer


def extrema_by(source: Observable,
               key_mapper: Mapper,
               comparer: SubComparer
               ) -> Observable:

    def subscribe(observer, scheduler=None):
        has_value = [False]
        last_key = [None]
        items = []

        def on_next(x):
            try:
                key = key_mapper(x)
            except Exception as ex:
                observer.on_error(ex)
                return

            comparison = 0

            if not has_value[0]:
                has_value[0] = True
                last_key[0] = key
            else:
                try:
                    comparison = comparer(key, last_key[0])
                except Exception as ex1:
                    observer.on_error(ex1)
                    return

            if comparison > 0:
                last_key[0] = key
                items[:] = []

            if comparison >= 0:
                items.append(x)

        def on_completed():
            observer.on_next(items)
            observer.on_completed()

        return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
    return Observable(subscribe)


def _min_by(key_mapper: Mapper,
            comparer: Optional[SubComparer] = None
            ) -> Callable[[Observable], Observable]:
    """The `min_by` operator.

    Returns the elements in an observable sequence with the minimum key
    value according to the specified comparer.

    Examples:
        >>> res = min_by(lambda x: x.value)
        >>> res = min_by(lambda x: x.value, lambda x, y: x - y)

    Args:
        key_mapper: Key mapper function.
        comparer: [Optional] Comparer used to compare key values.

    Returns:
        An observable sequence containing a list of zero or more
        elements that have a minimum key value.
    """

    cmp: SubComparer = comparer or default_sub_comparer

    def min_by(source: Observable) -> Observable:
        return extrema_by(source, key_mapper, lambda x, y: - cmp(x, y))
    return min_by
