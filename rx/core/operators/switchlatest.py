from typing import Callable

from rx import from_future
from rx.core import AnonymousObservable, Observable
from rx.disposables import CompositeDisposable, SingleAssignmentDisposable, SerialDisposable
from rx.internal.utils import is_future


def switch_latest() -> Callable[[Observable], Observable]:
    """Transforms an observable sequence of observable sequences into an
    observable sequence producing values only from the most recent
    observable sequence.

    Returns:
        An operator function that takes an observable source and returns
        the observable sequence that at any point in time produces the
        elements of the most recent inner observable sequence that has
        been received.
    """

    def partial(source: Observable) -> Observable:
        def subscribe(observer, scheduler=None):
            has_latest = [False]
            inner_subscription = SerialDisposable()
            is_stopped = [False]
            latest = [0]

            def on_next(inner_source):
                nonlocal source

                d = SingleAssignmentDisposable()
                with source.lock:
                    latest[0] += 1
                    _id = latest[0]
                has_latest[0] = True
                inner_subscription.disposable = d

                # Check if Future or Observable
                inner_source = from_future(inner_source) if is_future(inner_source) else inner_source

                def on_next(x):
                    if latest[0] == _id:
                        observer.on_next(x)

                def on_error(e):
                    if latest[0] == _id:
                        observer.on_error(e)

                def on_completed():
                    if latest[0] == _id:
                        has_latest[0] = False
                        if is_stopped[0]:
                            observer.on_completed()

                d.disposable = inner_source.subscribe_(on_next, on_error, on_completed, scheduler=scheduler)

            def on_completed():
                is_stopped[0] = True
                if not has_latest[0]:
                    observer.on_completed()

            subscription = source.subscribe_(on_next, observer.on_error, on_completed, scheduler=scheduler)
            return CompositeDisposable(subscription, inner_subscription)
        return AnonymousObservable(subscribe)
    return partial
