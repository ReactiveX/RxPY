from typing import Generic, TypeVar, cast

from reactivex import Observable, abc, typing
from reactivex.internal import curry_flip
from reactivex.internal.basic import default_comparer

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")


def array_index_of_comparer(
    array: list[_TKey], item: _TKey, comparer: typing.Comparer[_TKey]
):
    for i, a in enumerate(array):
        if comparer(a, item):
            return i
    return -1


class HashSet(Generic[_TKey]):
    def __init__(self, comparer: typing.Comparer[_TKey]):
        self.comparer = comparer
        self.set: list[_TKey] = []

    def push(self, value: _TKey):
        ret_value = array_index_of_comparer(self.set, value, self.comparer) == -1
        if ret_value:
            self.set.append(value)
        return ret_value


@curry_flip
def distinct_(
    source: Observable[_T],
    key_mapper: typing.Mapper[_T, _TKey] | None = None,
    comparer: typing.Comparer[_TKey] | None = None,
) -> Observable[_T]:
    """Returns an observable sequence that contains only distinct elements.

    Returns an observable sequence that contains only distinct
    elements according to the key_mapper and the comparer. Usage of
    this operator should be considered carefully due to the
    maintenance of an internal lookup structure which can grow large.

    Examples:
        >>> result = source.pipe(distinct())
        >>> result = distinct()(source)
        >>> result = source.pipe(distinct(lambda x: x.id))

    Args:
        source: Source observable to return distinct items from.
        key_mapper: Optional function to compute a comparison key.
        comparer: Optional equality comparer for computed keys.

    Returns:
        An observable sequence only containing the distinct
        elements, based on a computed key value, from the source
        sequence.
    """
    comparer_ = comparer or cast(typing.Comparer[_TKey], default_comparer)

    def subscribe(
        observer: abc.ObserverBase[_T],
        scheduler: abc.SchedulerBase | None = None,
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


__all__ = ["distinct_"]
