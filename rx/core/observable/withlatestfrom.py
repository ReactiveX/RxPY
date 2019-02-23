from rx.disposable import CompositeDisposable, SingleAssignmentDisposable

from rx.core import Observable
from rx.internal.utils import NotSet


def _with_latest_from(parent: Observable, *sources: Observable) -> Observable:
    NO_VALUE = NotSet()

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
        return CompositeDisposable(subscribe_all(parent, *sources))
    return Observable(subscribe)
