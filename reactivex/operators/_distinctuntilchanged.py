from typing import Callable, Optional, TypeVar, cast

from reactivex import Observable, abc
from reactivex.internal.basic import default_comparer, identity
from reactivex.typing import Comparer, Mapper

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")


def distinct_until_changed_(
    key_mapper: Optional[Mapper[_T, _TKey]] = None,
    comparer: Optional[Comparer[_TKey]] = None,
) -> Callable[[Observable[_T]], Observable[_T]]:

    key_mapper_ = key_mapper or cast(Callable[[_T], _TKey], identity)
    comparer_ = comparer or default_comparer

    def distinct_until_changed(source: Observable[_T]) -> Observable[_T]:
        """Returns an observable sequence that contains only distinct
        contiguous elements according to the key_mapper and the
        comparer.

        Examples:
            >>> op = distinct_until_changed();
            >>> op = distinct_until_changed(lambda x: x.id)
            >>> op = distinct_until_changed(lambda x: x.id, lambda x, y: x == y)

        Args:
            key_mapper: [Optional] A function to compute the comparison
                key for each element. If not provided, it projects the
                value.
            comparer: [Optional] Equality comparer for computed key
                values. If not provided, defaults to an equality
                comparer function.

        Returns:
            An observable sequence only containing the distinct
            contiguous elements, based on a computed key value, from
            the source sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            has_current_key = False
            current_key: _TKey = cast(_TKey, None)

            def on_next(value: _T) -> None:
                nonlocal has_current_key, current_key
                comparer_equals = False
                try:
                    key = key_mapper_(value)
                except Exception as exception:  # pylint: disable=broad-except
                    observer.on_error(exception)
                    return

                if has_current_key:
                    try:
                        comparer_equals = comparer_(current_key, key)
                    except Exception as exception:  # pylint: disable=broad-except
                        observer.on_error(exception)
                        return

                if not has_current_key or not comparer_equals:
                    has_current_key = True
                    current_key = key
                    observer.on_next(value)

            return source.subscribe(
                on_next, observer.on_error, observer.on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return distinct_until_changed


__all__ = ["distinct_until_changed_"]
