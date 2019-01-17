from rx.core import AnonymousObservable, Observable
from rx.internal.exceptions import SequenceContainsNoElementsError
from rx import operators as ops

def last_or_default_async(source, has_default=False, default_value=None):
    def subscribe(observer, scheduler=None):
        value = [default_value]
        seen_value = [False]

        def on_next(x):
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


def _last_or_default(predicate=None, default_value=None) -> Observable:
    def last_or_default(source: Observable) -> Observable:
        """Return last or default element.

        Examples:
            >>> res = _last_or_default(source)

        Args:
            source: Observable sequence to get the last item from.

        Returns:
            Observable sequence containing the last element in the
            observable sequence.
        """

        if predicate:
            return source.pipe(
                    ops.filter(predicate),
                    ops.last_or_default(None, default_value),
                    )

        return last_or_default_async(source, True, default_value)
    return last_or_default
