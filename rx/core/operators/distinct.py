from typing import Callable, Optional
from rx.core import Observable
from rx.core.typing import Mapper, Comparer
from rx.internal.basic import default_comparer


def array_index_of_comparer(array, item, comparer):
    for i, a in enumerate(array):
        if comparer(a, item):
            return i
    return -1


class HashSet:
    def __init__(self, comparer):
        self.comparer = comparer
        self.set = []

    def push(self, value):
        ret_value = array_index_of_comparer(self.set, value, self.comparer) == -1
        if ret_value:
            self.set.append(value)
        return ret_value


def _distinct(key_mapper: Optional[Mapper] = None,
              comparer: Optional[Comparer] = None
              ) -> Callable[[Observable], Observable]:
    comparer = comparer or default_comparer

    def distinct(source: Observable) -> Observable:
        """Returns an observable sequence that contains only distinct
        elements according to the key_mapper and the comparer. Usage of
        this operator should be considered carefully due to the maintenance
        of an internal lookup structure which can grow large.

        Examples:
            >>> res = obs = distinct(source)

        Args:
            source: Source observable to return distinct items from.

        Returns:
            An observable sequence only containing the distinct
            elements, based on a computed key value, from the source
            sequence.
        """

        def subscribe(observer, scheduler=None):
            hashset = HashSet(comparer)

            def on_next(x):
                key = x

                if key_mapper:
                    try:
                        key = key_mapper(x)
                    except Exception as ex:
                        observer.on_error(ex)
                        return

                hashset.push(key) and observer.on_next(x)
            return source.subscribe_(on_next, observer.on_error,observer.on_completed, scheduler)
        return Observable(subscribe)
    return distinct
