from time import sleep

from rx.internal import PriorityQueue
from rx.internal.constants import DELTA_ZERO

from .scheduleditem import ScheduledItem


class Trampoline(object):
    @classmethod
    def run(cls, queue: PriorityQueue[ScheduledItem]) -> None:
        while queue:
            item: ScheduledItem = queue.peek()
            if item.is_cancelled():
                queue.dequeue()
            else:
                diff = item.duetime - item.scheduler.now
                if diff <= DELTA_ZERO:
                    item.invoke()
                    queue.dequeue()
                else:
                    sleep(diff.total_seconds())
