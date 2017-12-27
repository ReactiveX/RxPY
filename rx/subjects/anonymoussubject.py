from typing import Any

from rx.core import ObservableBase, Observer, Disposable, Scheduler


class AnonymousSubject(ObservableBase, Observer):
    def __init__(self, observer: Observer, observable: ObservableBase) -> None:
        super().__init__()

        self.observer = observer
        self.observable = observable

    def _subscribe_core(self, observer: Observer, scheduler: Scheduler = None) -> Disposable:
        return self.observable.subscribe(observer, scheduler)

    def send(self, value: Any) -> None:
        self.observer.send(value)

    def throw(self, error: Exception) -> None:
        self.observer.throw(error)

    def close(self) -> None:
        self.observer.close()
