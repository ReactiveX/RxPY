from typing import Callable, Any, Optional

from rx.core import typing, Observable
from rx.core.typing import Mapper


def _to_dict(key_mapper: Mapper,
             element_mapper: Optional[Mapper] = None
             ) -> Callable[[Observable], Observable]:
    def to_dict(source: Observable) -> Observable:
        """Converts the observable sequence to a Map if it exists.

        Args:
            source: Source observable to convert.

        Returns:
            An observable sequence with a single value of a dictionary
            containing the values from the observable sequence.
        """

        def subscribe(observer: typing.Observer, scheduler: Optional[typing.Scheduler] = None) -> typing.Disposable:
            m = dict()

            def on_next(x: Any) -> None:
                try:
                    key = key_mapper(x)
                except Exception as ex:  # pylint: disable=broad-except
                    observer.on_error(ex)
                    return

                element = x
                if element_mapper:
                    try:
                        element = element_mapper(x)
                    except Exception as ex:  # pylint: disable=broad-except
                        observer.on_error(ex)
                        return

                m[key] = element

            def on_completed() -> None:
                nonlocal m
                observer.on_next(m)
                m = dict()
                observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
        return Observable(subscribe)
    return to_dict

