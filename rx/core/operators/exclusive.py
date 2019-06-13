from typing import Callable, Optional

import rx
from rx.core import Observable, typing
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable
from rx.internal.utils import is_future


def _exclusive() -> Callable[[Observable], Observable]:
    """Performs a exclusive waiting for the first to finish before
    subscribing to another observable. Observables that come in between
    subscriptions will be dropped on the floor.

    Returns:
        An exclusive observable with only the results that
        happen when subscribed.
    """

    def exclusive(source: Observable) -> Observable:
        def subscribe_observer(observer: typing.Observer,
                               scheduler: Optional[typing.Scheduler] = None
                               ) -> typing.Disposable:
            has_current = [False]
            is_stopped = [False]
            m = SingleAssignmentDisposable()
            g = CompositeDisposable()

            g.add(m)

            def on_next(inner_source):
                if not has_current[0]:
                    has_current[0] = True

                    inner_source = rx.from_future(inner_source) if is_future(inner_source) else inner_source

                    inner_subscription = SingleAssignmentDisposable()
                    g.add(inner_subscription)

                    def on_completed_inner():
                        g.remove(inner_subscription)
                        has_current[0] = False
                        if is_stopped[0] and len(g) == 1:
                            observer.on_completed()

                    inner_subscription.disposable = inner_source.subscribe(
                        observer.on_next,
                        observer.on_error,
                        on_completed_inner,
                        scheduler=scheduler
                    )

            def on_completed():
                is_stopped[0] = True
                if not has_current[0] and len(g) == 1:
                    observer.on_completed()

            m.disposable = source.subscribe(
                on_next,
                observer.on_error,
                on_completed,
                scheduler=scheduler
            )
            return g
        return Observable(subscribe_observer=subscribe_observer)
    return exclusive
