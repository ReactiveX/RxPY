from typing import Any, List, Optional, TypeVar

from reactivex import Observable, abc
from reactivex.disposable import Disposable
from reactivex.notification import Notification
from reactivex.scheduler import VirtualTimeScheduler

from .recorded import Recorded
from .subscription import Subscription

_T = TypeVar("_T")


class HotObservable(Observable[_T]):
    def __init__(
        self, scheduler: VirtualTimeScheduler, messages: List[Recorded[_T]]
    ) -> None:
        super().__init__()

        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions: List[Subscription] = []
        self.observers: List[abc.ObserverBase[_T]] = []

        observable = self

        def get_action(notification: Notification[_T]) -> abc.ScheduledAction[_T]:
            def action(scheduler: abc.SchedulerBase, state: Any) -> abc.DisposableBase:
                for observer in observable.observers[:]:
                    notification.accept(observer)
                return Disposable()

            return action

        for message in self.messages:
            notification = message.value
            if not isinstance(notification, Notification):
                raise ValueError("Must be notification")

            # Warning: Don't make closures within a loop
            action = get_action(notification)
            scheduler.schedule_absolute(message.time, action)

    def _subscribe_core(
        self,
        observer: Optional[abc.ObserverBase[_T]] = None,
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        if observer:
            self.observers.append(observer)
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1

        def dispose_action() -> None:
            if observer:
                self.observers.remove(observer)
            start = self.subscriptions[index].subscribe
            end = self.scheduler.clock
            self.subscriptions[index] = Subscription(start, end)

        return Disposable(dispose_action)
