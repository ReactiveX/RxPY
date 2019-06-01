import heapq
from sys import maxsize
from typing import Generic, List, Tuple

from rx.core.typing import T1


class PriorityQueue(Generic[T1]):
    """Priority queue for scheduling. Note that methods aren't thread-safe."""

    MIN_COUNT = ~maxsize

    def __init__(self) -> None:
        self.items: List[Tuple[T1, int]] = []
        self.count = PriorityQueue.MIN_COUNT  # Monotonic increasing for sort stability

    def __len__(self):
        """Returns length of queue"""

        return len(self.items)

    def peek(self) -> T1:
        """Returns first item in queue without removing it"""
        return self.items[0][0]

    def dequeue(self) -> T1:
        """Returns and removes item with lowest priority from queue"""

        item: T1 = heapq.heappop(self.items)[0]
        if not self.items:
            self.count = PriorityQueue.MIN_COUNT
        return item

    def enqueue(self, item: T1) -> None:
        """Adds item to queue"""

        heapq.heappush(self.items, (item, self.count))
        self.count += 1

    def remove(self, item: T1) -> bool:
        """Remove given item from queue"""

        for index, _item in enumerate(self.items):
            if _item[0] == item:
                self.items.pop(index)
                heapq.heapify(self.items)
                return True

        return False

    def clear(self):
        """Remove all items from the queue."""
        self.items = []
        self.count = PriorityQueue.MIN_COUNT
