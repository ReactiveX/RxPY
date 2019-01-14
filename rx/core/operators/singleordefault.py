from rx import operators as ops
from rx.core import Observable, AnonymousObservable, pipe
from rx.core.typing import Predicate, Any
from rx.internal.exceptions import SequenceContainsNoElementsError


def _single_or_default_async(has_default: bool = False, default_value: Any = None):
    def single_or_default_async(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            value = [default_value]
            seen_value = [False]

            def on_next(x):
                if seen_value[0]:
                    observer.on_error(Exception('Sequence contains more than one element'))
                else:
                    value[0] = x
                    seen_value[0] = True

            def on_completed():
                if not seen_value[0] and not has_default:
                    observer.on_error(SequenceContainsNoElementsError())
                else:
                    observer.on_next(value[0])
                    observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return single_or_default_async


def _single_or_default(predicate: Predicate = None, default_value: Any = None) -> Observable:
    """Returns the only element of an observable sequence that matches
    the predicate, or a default value if no such element exists this
    method reports an exception if there is more than one element in the
    observable sequence.

    Examples:
        >>> res = single_or_default()
        >>> res = single_or_default(lambda x: x == 42)
        >>> res = single_or_default(lambda x: x == 42, 0)
        >>> res = single_or_default(None, 0)

    Args:
        predicate -- [Optional] A predicate function to evaluate for
            elements in the source sequence.
        default_value -- [Optional] The default value if the index is
            outside the bounds of the source sequence.

    Returns:
        An observable Sequence containing the single element in the
    observable sequence that satisfies the condition in the predicate,
    or a default value if no such element exists.
    """

    if predicate:
        return pipe(ops.filter(predicate), ops.single_or_default(None, default_value))
    else:
        return _single_or_default_async(True, default_value)
