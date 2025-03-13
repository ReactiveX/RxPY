from typing import Callable, Dict, Optional, TypeVar, cast

from reactivex import Observable, abc
from reactivex.typing import Mapper

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")
_TValue = TypeVar("_TValue")


def to_dict_(
    key_mapper: Mapper[_T, _TKey], element_mapper: Optional[Mapper[_T, _TValue]] = None
) -> Callable[[Observable[_T]], Observable[Dict[_TKey, _TValue]]]:
    def to_dict(source: Observable[_T]) -> Observable[Dict[_TKey, _TValue]]:
        """Converts the observable sequence to a Map if it exists.

        Args:
            source: Source observable to convert.

        Returns:
            An observable sequence with a single value of a dictionary
            containing the values from the observable sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[Dict[_TKey, _TValue]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            m: Dict[_TKey, _TValue] = dict()

            def on_next(x: _T) -> None:
                try:
                    key = key_mapper(x)
                except Exception as ex:  # pylint: disable=broad-except
                    observer.on_error(ex)
                    return

                if element_mapper:
                    try:
                        element = element_mapper(x)
                    except Exception as ex:  # pylint: disable=broad-except
                        observer.on_error(ex)
                        return
                else:
                    element = cast(_TValue, x)

                m[key] = element

            def on_completed() -> None:
                nonlocal m
                observer.on_next(m)
                m = dict()
                observer.on_completed()

            return source.subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return to_dict


__all__ = ["to_dict_"]
