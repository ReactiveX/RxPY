from typing import Any

from rx.core import Observable, Observer, AnonymousObservable
from rx.concurrency import immediate_scheduler
from rx.core.bases.scheduler import Scheduler


def empty() -> Observable:
    """Returns an empty observable sequence.

    1 - res = rx.Observable.empty()

    Returns an observable sequence with no elements.
    """

    def subscribe(observer: Observer, scheduler: Scheduler=None) -> Observable:
        scheduler = scheduler or immediate_scheduler

        def action(_: Scheduler, __: Any) -> None:
            observer.close()

        return scheduler.schedule(action)
    return AnonymousObservable(subscribe)
