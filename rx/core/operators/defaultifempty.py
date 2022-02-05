from typing import Any, Callable, Optional, TypeVar

from rx.core import Observable, abc

_T = TypeVar("_T")


def default_if_empty_(
    default_value: _T = None,
) -> Callable[[Observable[_T]], Observable[_T]]:
    def default_if_empty(source: Observable[_T]) -> Observable[_T]:
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
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            found = [False]

            def on_next(x: _T):
                found[0] = True
                observer.on_next(x)

            def on_completed():
                if not found[0]:
                    observer.on_next(default_value)
                observer.on_completed()

            return source.subscribe_(
                on_next, observer.on_error, on_completed, scheduler
            )

        return Observable(subscribe)

    return default_if_empty


__all__ = ["default_if_empty_"]
