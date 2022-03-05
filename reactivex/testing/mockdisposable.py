from typing import List

from reactivex import abc, typing
from reactivex.scheduler import VirtualTimeScheduler


class MockDisposable(abc.DisposableBase):
    def __init__(self, scheduler: VirtualTimeScheduler):
        self.scheduler = scheduler
        self.disposes: List[typing.AbsoluteTime] = []
        self.disposes.append(self.scheduler.clock)

    def dispose(self) -> None:
        self.disposes.append(self.scheduler.clock)
