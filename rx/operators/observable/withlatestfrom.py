from typing import Any, Iterable, Callable, Union
from rx.core import ObservableBase, AnonymousObservable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable


def with_latest_from(observables: Union[ObservableBase, Iterable[ObservableBase]],
                     selector: Callable[[Any], Any]) -> ObservableBase:
    """With latest from operator.

    Merges the specified observable sequences into one observable
    sequence by using the selector function only when the first
    observable sequence produces an element. The observables can be
    passed either as seperate arguments or as a list.

    1 - obs = Observable.with_latest_from(obs1, lambda o1: o1)

    2 - obs = Observable.with_latest_from([obs1, obs2, obs3],
                                        lambda o1, o2, o3: o1 + o2 + o3)

    Returns an observable sequence containing the result of combining
    elements of the sources using the specified result selector
    function.
    """
    if isinstance(observables, ObservableBase):
        observables = [observables]

    result_selector = selector
    NO_VALUE = object()

    def subscribe(observer, scheduler=None):

        def subscribe_all(parent, *children):

            values = [NO_VALUE for _ in children]

            def subscribe_child(i, child):
                subscription = SingleAssignmentDisposable()

                def send(value):
                    with parent.lock:
                        values[i] = value
                subscription.disposable = child.subscribe_callbacks(
                    send, observer.throw, scheduler=scheduler)
                return subscription

            parent_subscription = SingleAssignmentDisposable()

            def send(value):
                with parent.lock:
                    if NO_VALUE not in values:
                        try:
                            result = result_selector(value, *values)
                        except Exception as error:
                            observer.throw(error)
                        else:
                            observer.send(result)
            parent_subscription.disposable = parent.subscribe_callbacks(
                send, observer.throw, observer.close, scheduler)

            children_subscription = [subscribe_child(i, child) for i, child in enumerate(children)]

            return [parent_subscription] + children_subscription
        return CompositeDisposable(subscribe_all(*observables))
    return AnonymousObservable(subscribe)
