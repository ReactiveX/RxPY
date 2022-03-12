from collections import deque
from threading import Condition, Lock
from typing import Deque

from reactivex.internal.priorityqueue import PriorityQueue

from .scheduleditem import ScheduledItem


class Trampoline:
    def __init__(self) -> None:
        self._idle: bool = True
        self._queue: PriorityQueue[ScheduledItem] = PriorityQueue()
        self._lock: Lock = Lock()
        self._condition: Condition = Condition(self._lock)

    def idle(self) -> bool:
        with self._lock:
            return self._idle

    def run(self, item: ScheduledItem) -> None:
        with self._lock:
            self._queue.enqueue(item)
            if self._idle:
                self._idle = False
            else:
                self._condition.notify()
                return
        try:
            self._run()
        finally:
            with self._lock:
                self._idle = True
                self._queue.clear()

    def _run(self) -> None:
        ready: Deque[ScheduledItem] = deque()
        while True:
            with self._lock:
                while len(self._queue) > 0:
                    item: ScheduledItem = self._queue.peek()
                    if item.duetime <= item.scheduler.now:
                        self._queue.dequeue()
                        ready.append(item)
                    else:
                        break

            while len(ready) > 0:
                item = ready.popleft()
                if not item.is_cancelled():
                    item.invoke()

            with self._lock:
                if len(self._queue) == 0:
                    break
                item = self._queue.peek()
                seconds = (item.duetime - item.scheduler.now).total_seconds()
                if seconds > 0.0:
                    self._condition.wait(seconds)


__all__ = ["Trampoline"]
