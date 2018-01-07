from rx.core import ObservableBase, AnonymousObservable
from rx.core.typing import Predicate, Any
from rx.internal.exceptions import SequenceContainsNoElementsError


def single_or_default_async(source: ObservableBase, has_default: bool = False, default_value: Any = None):
    def subscribe(observer, scheduler=None):
        value = [default_value]
        seen_value = [False]

        def send(x):
            if seen_value[0]:
                observer.throw(Exception('Sequence contains more than one element'))
            else:
                value[0] = x
                seen_value[0] = True

        def close():
            if not seen_value[0] and not has_default:
                observer.throw(SequenceContainsNoElementsError())
            else:
                observer.send(value[0])
                observer.close()

        return source.subscribe_(send, observer.throw, close, scheduler)
    return AnonymousObservable(subscribe)

def single_or_default(source: ObservableBase, predicate: Predicate = None,
                      default_value: Any = None) -> ObservableBase:
    """Returns the only element of an observable sequence that matches
    the predicate, or a default value if no such element exists this
    method reports an exception if there is more than one element in the
    observable sequence.

    Example:
    res = source.single_or_default()
    res = source.single_or_default(lambda x: x == 42)
    res = source.single_or_default(lambda x: x == 42, 0)
    res = source.single_or_default(None, 0)

    Keyword arguments:
    predicate -- [Optional] A predicate function to evaluate for
        elements in the source sequence.
    default_value -- [Optional] The default value if the index is
        outside the bounds of the source sequence.

    Returns observable Sequence containing the single element in the
    observable sequence that satisfies the condition in the predicate,
    or a default value if no such element exists.
    """

    return source.filter(predicate).single_or_default(None, default_value) if predicate else single_or_default_async(source, True, default_value)
