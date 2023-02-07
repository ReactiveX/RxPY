from typing import Dict, Optional, TypeVar, cast

from reactivex import Observable, abc
from reactivex.typing import Mapper
from reactivex.curry import curry_flip

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")
_TValue = TypeVar("_TValue")


@curry_flip(1)
def to_dict_(
    source: Observable[_T],
    key_mapper: Mapper[_T, _TKey],
    element_mapper: Optional[Mapper[_T, _TValue]] = None,
) -> Observable[Dict[_TKey, _TValue]]:
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

            m[key] = cast(_TValue, element)

        def on_completed() -> None:
            nonlocal m
            observer.on_next(m)
            m = dict()
            observer.on_completed()

        return source.subscribe(
            on_next, observer.on_error, on_completed, scheduler=scheduler
        )

    return Observable(subscribe)


__all__ = ["to_dict_"]
