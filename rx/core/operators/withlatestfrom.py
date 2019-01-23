from typing import Any, Iterable, Callable, Union, List, cast

from rx.core import Observable, AnonymousObservable
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable



def _with_latest_from(*args: Union[Observable, Iterable[Observable]]
                      ) -> Callable[[Observable], Observable]:
    """With latest from operator.

    Merges the specified observable sequences into one observable
    sequence by creating a tuple only when the first
    observable sequence produces an element. The observables can be
    passed either as seperate arguments or as a list.

    Examples:
        >>> op = with_latest_from(obs1)
        >>> op = with_latest_from([obs1, obs2, obs3])

    Returns:
        An observable sequence containing the result of combining
    elements of the sources into a tuple.
    """

    def with_latest_from(source: Observable) -> Observable:
        sources: List[Observable] = [source]

        if isinstance(args[0], Iterable):
            sources = list(args[0])
        else:
            sources = cast(List[Observable], list(args))

        NO_VALUE = object()

        def subscribe(observer, scheduler=None):
            def subscribe_all(parent, *children):

                values = [NO_VALUE for _ in children]

                def subscribe_child(i, child):
                    subscription = SingleAssignmentDisposable()

                    def on_next(value):
                        with parent.lock:
                            values[i] = value
                    subscription.disposable = child.subscribe_(on_next, observer.on_error, scheduler=scheduler)
                    return subscription

                parent_subscription = SingleAssignmentDisposable()

                def on_next(value):
                    with parent.lock:
                        if NO_VALUE not in values:
                            result = (value,) + tuple(values)
                            observer.on_next(result)

                disp = parent.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
                parent_subscription.disposable = disp

                children_subscription = [subscribe_child(i, child) for i, child in enumerate(children)]

                return [parent_subscription] + children_subscription
            return CompositeDisposable(subscribe_all(source, *sources))
        return AnonymousObservable(subscribe)
    return with_latest_from
