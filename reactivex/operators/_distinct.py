from typing import Callable, Generic, List, Optional, TypeVar, cast

from reactivex import Observable, abc, typing
from reactivex.internal.basic import default_comparer

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")


def array_index_of_comparer(
    array: List[_TKey], item: _TKey, comparer: typing.Comparer[_TKey]
):
    for i, a in enumerate(array):
        if comparer(a, item):
            return i
    return -1


class HashSet(Generic[_TKey]):
    def __init__(self, comparer: typing.Comparer[_TKey]):
        self.comparer = comparer
        self.set: List[_TKey] = []

    def push(self, value: _TKey):
        ret_value = array_index_of_comparer(self.set, value, self.comparer) == -1
        if ret_value:
            self.set.append(value)
        return ret_value


def distinct_(
    key_mapper: Optional[typing.Mapper[_T, _TKey]] = None,
    comparer: Optional[typing.Comparer[_TKey]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    comparer_ = comparer or cast(typing.Comparer[_TKey], default_comparer)

    def distinct(source: Observable[_T]) -> Observable[_T]:
        """Returns an observable sequence that contains only distinct
        elements according to the key_mapper and the comparer. Usage of
        this operator should be considered carefully due to the
        maintenance of an internal lookup structure which can grow
        large.

        Examples:
            >>> res = obs = distinct(source)

        Args:
            source: Source observable to return distinct items from.

        Returns:
            An observable sequence only containing the distinct
            elements, based on a computed key value, from the source
            sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            hashset = HashSet(comparer_)

            def on_next(x: _T) -> None:
                key = cast(_TKey, x)

                if key_mapper:
                    try:
                        key = key_mapper(x)
                    except Exception as ex:
                        observer.on_error(ex)
                        return

                if hashset.push(key):
                    observer.on_next(x)

            return source.subscribe(
                on_next, observer.on_error, observer.on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return distinct


__all__ = ["distinct_"]
