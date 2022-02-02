from typing import Any, Callable, Optional, TypeVar

from rx import operators as ops
from rx.core import Observable, abc, pipe
from rx.core.typing import Predicate
from rx.internal.exceptions import SequenceContainsNoElementsError

_T = TypeVar("_T")


def _first_or_default_async(
    has_default: bool = False, default_value: Optional[_T] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    def first_or_default_async(source: Observable[_T]) -> Observable[_T]:
        def subscribe(observer: abc.ObserverBase[_T], scheduler: Optional[abc.SchedulerBase] = None):
            def on_next(x: _T):
                observer.on_next(x)
                observer.on_completed()

            def on_completed():
                if not has_default:
                    observer.on_error(SequenceContainsNoElementsError())
                else:
                    observer.on_next(default_value)
                    observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)

        return Observable(subscribe)

    return first_or_default_async


def _first_or_default(
    predicate: Optional[Predicate[_T]] = None, default_value: Optional[_T] = None
) -> Callable[[Observable[_T]], Observable[_T]]:
    """Returns the first element of an observable sequence that
    satisfies the condition in the predicate, or a default value if no
    such element exists.

    Examples:
        >>> res = source.first_or_default()
        >>> res = source.first_or_default(lambda x: x > 3)
        >>> res = source.first_or_default(lambda x: x > 3, 0)
        >>> res = source.first_or_default(None, 0)

    Args:
        source -- Observable sequence.
        predicate -- [optional] A predicate function to evaluate for
            elements in the source sequence.
        default_value -- [Optional] The default value if no such element
            exists.  If not specified, defaults to None.

    Returns:
        A function that takes an observable source and reutrn an
        observable sequence containing the first element in the
        observable sequence that satisfies the condition in the
        predicate, or a default value if no such element exists.
    """

    if predicate:
        return pipe(ops.filter(predicate), ops.first_or_default(None, default_value))
    return _first_or_default_async(True, default_value)


__all__ = ["_first_or_default", "_first_or_default_async"]
