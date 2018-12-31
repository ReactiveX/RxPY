from typing import Any, Iterable, Callable, Union
from rx.core import ObservableBase, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable


def with_latest_from(observables: Union[ObservableBase, Iterable[ObservableBase]],
                     mapper: Callable[[Any], Any]) -> ObservableBase:
    """With latest from operator.

    Merges the specified observable sequences into one observable
    sequence by using the mapper function only when the first
    observable sequence produces an element. The observables can be
    passed either as seperate arguments or as a list.

    1 - obs = Observable.with_latest_from(obs1, lambda o1: o1)

    2 - obs = Observable.with_latest_from([obs1, obs2, obs3],
                                        lambda o1, o2, o3: o1 + o2 + o3)

    Returns an observable sequence containing the result of combining
    elements of the sources using the specified result mapper
    function.
    """
    if isinstance(observables, ObservableBase):
        observables = [observables]

    result_mapper = mapper
    NO_VALUE = object()

    def subscribe(observer, scheduler=None):

        def subscribe_all(parent, *children):

            values = [NO_VALUE for _ in children]

            def subscribe_child(i, child):
                subscription = SingleAssignmentDisposable()

                def on_next(value):
                    with parent.lock:
                        values[i] = value
                subscription.disposable = child.subscribe_(
                    on_next, observer.on_error, scheduler=scheduler)
                return subscription

            parent_subscription = SingleAssignmentDisposable()

            def on_next(value):
                with parent.lock:
                    if NO_VALUE not in values:
                        try:
                            result = result_mapper(value, *values)
                        except Exception as error:
                            observer.on_error(error)
                        else:
                            observer.on_next(result)
            parent_subscription.disposable = parent.subscribe_(
                on_next, observer.on_error, observer.on_completed, scheduler)

            children_subscription = [subscribe_child(i, child) for i, child in enumerate(children)]

            return [parent_subscription] + children_subscription
        return CompositeDisposable(subscribe_all(*observables))
    return AnonymousObservable(subscribe)
