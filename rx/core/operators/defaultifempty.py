from typing import Any, Callable
from rx.core import AnonymousObservable, ObservableBase as Observable
from rx.core.typing import Disposable


def default_if_empty(default_value: Any = None) -> Callable[[Observable], Observable]:
    """Returns the elements of the specified sequence or the specified
    value in a singleton sequence if the sequence is empty.

    Examples:
        >>> res = obs = default_if_empty()(xs)
        >>> obs = default_if_empty(False)(xs)

    Args:
        default_value: The value to return if the sequence is empty. If
        not provided, this defaults to None.

    Returns:
        An observable sequence that contains the specified default value
        if the source is empty otherwise, the elements of the source.
    """

    def partial(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None) -> Disposable:
            found = [False]

            def on_next(x: Any):
                found[0] = True
                observer.on_next(x)

            def on_completed():
                if not found[0]:
                    observer.on_next(default_value)
                observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return partial
