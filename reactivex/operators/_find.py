from typing import Callable, Optional, TypeVar, Union

from reactivex import Observable, abc

_T = TypeVar("_T")


def find_value_(
    predicate: Callable[[_T, int, Observable[_T]], bool], yield_index: bool
) -> Callable[[Observable[_T]], Observable[Union[_T, int, None]]]:
    def find_value(source: Observable[_T]) -> Observable[Union[_T, int, None]]:
        def subscribe(
            observer: abc.ObserverBase[Union[_T, int, None]],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            index = 0

            def on_next(x: _T) -> None:
                nonlocal index
                should_run = False
                try:
                    should_run = predicate(x, index, source)
                except Exception as ex:  # pylint: disable=broad-except
                    observer.on_error(ex)
                    return

                if should_run:
                    observer.on_next(index if yield_index else x)
                    observer.on_completed()
                else:
                    index += 1

            def on_completed():
                observer.on_next(-1 if yield_index else None)
                observer.on_completed()

            return source.subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return find_value


__all__ = ["find_value_"]
