from typing import Callable, Optional, TypeVar

from reactivex import Observable, abc
from reactivex import operators as ops
from reactivex.typing import Predicate

_T = TypeVar("_T")


def some_(
    predicate: Optional[Predicate[_T]] = None,
) -> Callable[[Observable[_T]], Observable[bool]]:
    def some(source: Observable[_T]) -> Observable[bool]:
        """Partially applied operator.

        Determines whether some element of an observable sequence satisfies a
        condition if present, else if some items are in the sequence.

        Example:
            >>> obs = some(source)

        Args:
            predicate -- A function to test each element for a condition.

        Returns:
            An observable sequence containing a single element
            determining whether some elements in the source sequence
            pass the test in the specified predicate if given, else if
            some items are in the sequence.
        """

        def subscribe(
            observer: abc.ObserverBase[bool],
            scheduler: Optional[abc.SchedulerBase] = None,
        ):
            def on_next(_: _T):
                observer.on_next(True)
                observer.on_completed()

            def on_error():
                observer.on_next(False)
                observer.on_completed()

            return source.subscribe(
                on_next, observer.on_error, on_error, scheduler=scheduler
            )

        if predicate:
            return source.pipe(
                ops.filter(predicate),
                some_(),
            )

        return Observable(subscribe)

    return some


__all__ = ["some_"]
