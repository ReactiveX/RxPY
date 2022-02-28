from typing import Any, List, Optional, TypeVar

from reactivex import Notification, Observable, abc
from reactivex.disposable import CompositeDisposable, Disposable
from reactivex.scheduler import VirtualTimeScheduler

from .recorded import Recorded
from .subscription import Subscription

_T = TypeVar("_T")


class ColdObservable(Observable[_T]):
    def __init__(
        self, scheduler: VirtualTimeScheduler, messages: List[Recorded[_T]]
    ) -> None:
        super().__init__()

        self.scheduler = scheduler
        self.messages = messages
        self.subscriptions: List[Subscription] = []

    def _subscribe_core(
        self,
        observer: Optional[abc.ObserverBase[_T]] = None,
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        self.subscriptions.append(Subscription(self.scheduler.clock))
        index = len(self.subscriptions) - 1
        disp = CompositeDisposable()

        def get_action(notification: Notification[_T]) -> abc.ScheduledAction[_T]:
            def action(
                scheduler: abc.SchedulerBase, state: Any = None
            ) -> abc.DisposableBase:
                if observer:
                    notification.accept(observer)
                return Disposable()

            return action

        for message in self.messages:
            notification = message.value
            if not isinstance(notification, Notification):
                raise ValueError("Must be notification")

            # Don't make closures within a loop
            action = get_action(notification)
            disp.add(self.scheduler.schedule_relative(message.time, action))

        def dispose() -> None:
            start = self.subscriptions[index].subscribe
            end = self.scheduler.to_seconds(self.scheduler.now)
            self.subscriptions[index] = Subscription(start, int(end))
            disp.dispose()

        return Disposable(dispose)
