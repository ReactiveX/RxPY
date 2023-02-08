from typing import Optional, TypeVar

from reactivex import Observable, abc, operators
from reactivex.typing import Predicate, PredicateIndexed
from reactivex.curry import curry_flip

_T = TypeVar("_T")


@curry_flip(1)
def take_while_(
    source: Observable[_T], predicate: Predicate[_T], inclusive: bool = False
) -> Observable[_T]:
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


@curry_flip(1)
def take_while_indexed_(
    source: Observable[_T], predicate: PredicateIndexed[_T], inclusive: bool = False
) -> Observable[_T]:
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
    i = 0

    def increment(_: _T):
        nonlocal i
        i += 1

    def predicate_with_index(x: _T):
        return predicate(x, i)

    return source.pipe(
        take_while_(predicate_with_index, inclusive=inclusive),
        operators.do_action(on_next=increment),
    )


__all__ = ["take_while_", "take_while_indexed_"]
