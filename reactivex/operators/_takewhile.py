from typing import Any, Callable, Optional, TypeVar

from reactivex import Observable, abc
from reactivex.typing import Predicate, PredicateIndexed

_T = TypeVar("_T")


def take_while_(
    predicate: Predicate[_T], inclusive: bool = False
) -> Callable[[Observable[_T]], Observable[_T]]:
    def take_while(source: Observable[_T]) -> Observable[_T]:
        """Returns elements from an observable sequence as long as a
        specified condition is true.

        Example:
            >>> take_while(source)

        Args:
            source: The source observable to take from.

        Returns:
            An observable sequence that contains the elements from the
            input sequence that occur before the element at which the
            test no longer passes.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            running = True

            def on_next(value: _T):
                nonlocal running

                with source.lock:
                    if not running:
                        return

                    try:
                        running = predicate(value)
                    except Exception as exn:
                        observer.on_error(exn)
                        return

                if running:
                    observer.on_next(value)
                else:
                    if inclusive:
                        observer.on_next(value)
                    observer.on_completed()

            return source.subscribe(
                on_next, observer.on_error, observer.on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return take_while


def take_while_indexed_(
    predicate: PredicateIndexed[_T], inclusive: bool = False
) -> Callable[[Observable[_T]], Observable[_T]]:
    def take_while_indexed(source: Observable[_T]) -> Observable[_T]:
        """Returns elements from an observable sequence as long as a
        specified condition is true. The element's index is used in the
        logic of the predicate function.

        Example:
            >>> take_while(source)

        Args:
            source: Source observable to take from.

        Returns:
            An observable sequence that contains the elements from the
            input sequence that occur before the element at which the
            test no longer passes.
        """

        def subscribe(
            observer: abc.ObserverBase[_T],
            scheduler: Optional[abc.SchedulerBase] = None,
        ) -> abc.DisposableBase:
            running = True
            i = 0

            def on_next(value: Any) -> None:
                nonlocal running, i

                with source.lock:
                    if not running:
                        return

                    try:
                        running = predicate(value, i)
                    except Exception as exn:
                        observer.on_error(exn)
                        return
                    else:
                        i += 1

                if running:
                    observer.on_next(value)
                else:
                    if inclusive:
                        observer.on_next(value)
                    observer.on_completed()

            return source.subscribe(
                on_next, observer.on_error, observer.on_completed, scheduler=scheduler
            )

        return Observable(subscribe)

    return take_while_indexed


__all__ = ["take_while_", "take_while_indexed_"]
