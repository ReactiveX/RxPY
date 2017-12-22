from rx.core import ObservableBase


def let(self, func, *args, **kwargs) -> ObservableBase:
    """Returns an observable sequence that is the result of invoking the
    selector on the source sequence, without sharing subscriptions. This
    operator allows for a fluent style of writing queries that use the
    same sequence multiple times.

    selector -- Selector function which can use the source
        sequence as many times as needed, without sharing subscriptions to
        the source sequence.

    Returns an observable sequence that contains the elements of a
    sequence produced by multicasting the source sequence within a
    selector function.

    Any kwargs given will be passed through to the selector. This allows
    for a clean syntax when composing with parameterized selectors.
    """

    return func(self, *args, **kwargs)
