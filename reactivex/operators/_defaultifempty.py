from collections.abc import Callable
from typing import TypeVar

from reactivex import Observable, abc

_T = TypeVar("_T")


def default_if_empty_(
    default_value: _T | None = None,
) -> Callable[[Observable[_T]], Observable[_T | None]]:
    def default_if_empty(source: Observable[_T]) -> Observable[_T | None]:
        """Returns the elements of the specified sequence or the
        specified value in a singleton sequence if the sequence is
        empty.

        Examples:
            >>> obs = default_if_empty(source)

        Args:
            source: Source observable.

        Returns:
            An observable sequence that contains the specified default
            value if the source is empty otherwise, the elements of the
            source.
        """

        def subscribe(
            observer: abc.ObserverBase[_T | None],
            scheduler: abc.SchedulerBase | None = None,
        ) -> abc.DisposableBase:
            found = [False]

            def on_next(x: _T):
                found[0] = True
                observer.on_next(x)

            def on_completed():
                if not found[0]:
                    observer.on_next(default_value)
                observer.on_completed()

            return source.subscribe(
                on_next, observer.on_error, on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return default_if_empty


__all__ = ["default_if_empty_"]
