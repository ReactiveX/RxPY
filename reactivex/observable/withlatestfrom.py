from typing import Any, List, Optional, Tuple

from reactivex import Observable, abc
from reactivex.disposable import CompositeDisposable, SingleAssignmentDisposable
from reactivex.internal.utils import NotSet


def with_latest_from_(
    parent: Observable[Any], *sources: Observable[Any]
) -> Observable[Tuple[Any, ...]]:
    NO_VALUE = NotSet()

    def subscribe(
        observer: abc.ObserverBase[Any], scheduler: Optional[abc.SchedulerBase] = None
    ) -> abc.DisposableBase:
        def subscribeall(
            parent: Observable[Any], *children: Observable[Any]
        ) -> List[SingleAssignmentDisposable]:

            values = [NO_VALUE for _ in children]

            def subscribechild(
                i: int, child: Observable[Any]
            ) -> SingleAssignmentDisposable:
                subscription = SingleAssignmentDisposable()

                def on_next(value: Any) -> None:
                    with parent.lock:
                        values[i] = value

                subscription.disposable = child.subscribe(
                    on_next, observer.on_error, scheduler=scheduler
                )
                return subscription

            parent_subscription = SingleAssignmentDisposable()

            def on_next(value: Any) -> None:
                with parent.lock:
                    if NO_VALUE not in values:
                        result = (value,) + tuple(values)
                        observer.on_next(result)

            children_subscription = [
                subscribechild(i, child) for i, child in enumerate(children)
            ]
            disp = parent.subscribe(
                on_next, observer.on_error, observer.on_completed, scheduler=scheduler
            )
            parent_subscription.disposable = disp

            return [parent_subscription] + children_subscription

        return CompositeDisposable(subscribeall(parent, *sources))

    return Observable(subscribe)


__all__ = ["with_latest_from_"]
