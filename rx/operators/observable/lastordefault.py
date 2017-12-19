from rx.core import AnonymousObservable, ObservableBase
from rx.internal.exceptions import SequenceContainsNoElementsError


def last_or_default_async(source, has_default=False, default_value=None):
    def subscribe(observer, scheduler=None):
        value = [default_value]
        seen_value = [False]

        def send(x):
            value[0] = x
            seen_value[0] = True

        def close():
            if not seen_value[0] and not has_default:
                observer.throw(SequenceContainsNoElementsError())
            else:
                observer.send(value[0])
                observer.close()

        return source.subscribe_callbacks(send, observer.throw, close, scheduler)
    return AnonymousObservable(subscribe)


def last_or_default(self, predicate=None, default_value=None) -> ObservableBase:
    """Return last or default element.

    Returns the last element of an observable sequence that satisfies
    the condition in the predicate, or a default value if no such
    element exists.

    Examples:
    res = source.last_or_default()
    res = source.last_or_default(lambda x: x > 3)
    res = source.last_or_default(lambda x: x > 3, 0)
    res = source.last_or_default(None, 0)

    predicate -- [Optional] A predicate function to evaluate for
        elements in the source sequence.
    default_value -- [Optional] The default value if no such element
        exists. If not specified, defaults to None.

    Returns Observable sequence containing the last element in the
    observable sequence that satisfies the condition in the predicate,
    or a default value if no such element exists.
    """
    if predicate:
        return self.filter(predicate).last_or_default(None, default_value)

    return last_or_default_async(self, True, default_value)
