from typing import Any, Optional

from rx.core import typing
from rx.core import Observable
from rx.core.typing import Observer, Scheduler


class AnonymousSubject(Observable, Observer):
    def __init__(self, observer: Observer, observable: Observable) -> None:
        super().__init__()

        self.observer = observer
        self.observable = observable

    def _subscribe_core(self, observer: Observer, scheduler: Optional[Scheduler] = None) -> typing.Disposable:
        return self.observable.subscribe(observer, scheduler=scheduler)

    def on_next(self, value: Any) -> None:
        self.observer.on_next(value)

    def on_error(self, error: Exception) -> None:
        self.observer.on_error(error)

    def on_completed(self) -> None:
        self.observer.on_completed()
