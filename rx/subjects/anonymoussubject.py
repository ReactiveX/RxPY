from typing import Any

from rx.core import ObservableBase, Observer, Disposable, Scheduler


class AnonymousSubject(ObservableBase, Observer):
    def __init__(self, observer: Observer, observable: ObservableBase) -> None:
        super().__init__()

        self.observer = observer
        self.observable = observable

    def _subscribe_core(self, observer: Observer, scheduler: Scheduler = None) -> Disposable:
        return self.observable.subscribe(observer, scheduler)

    def on_next(self, value: Any) -> None:
        self.observer.on_next(value)

    def on_error(self, error: Exception) -> None:
        self.observer.on_error(error)

    def on_completed(self) -> None:
        self.observer.on_completed()
