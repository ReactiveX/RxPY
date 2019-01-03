import heapq
from typing import List, Any
from threading import RLock

from rx.internal.exceptions import InvalidOperationException


class PriorityQueue:
    """Priority queue for scheduling"""

    def __init__(self, capacity=None) -> None:
        self.items: List[Any] = []
        self.count = 0  # Monotonic increasing for sort stability

        self.lock = RLock()

    def __len__(self):
        """Returns length of queue"""

        return len(self.items)

    def peek(self) -> Any:
        """Returns first item in queue without removing it"""
        try:
            return self.items[0][0]
        except IndexError:
            raise InvalidOperationException("Queue is empty")

    def remove_at(self, index: int) -> Any:
        """Removes item at given index"""

        with self.lock:
            item = self.items.pop(index)[0]
            heapq.heapify(self.items)
        return item

    def dequeue(self) -> Any:
        """Returns and removes item with lowest priority from queue"""

        with self.lock:
            item = heapq.heappop(self.items)[0]
        return item

    def enqueue(self, item: Any) -> None:
        """Adds item to queue"""

        with self.lock:
            heapq.heappush(self.items, (item, self.count))
            self.count += 1

    def remove(self, item: Any) -> bool:
        """Remove given item from queue"""

        with self.lock:
            for index, _item in enumerate(self.items):
                if _item[0] == item:
                    self.items.pop(index)
                    heapq.heapify(self.items)
                    return True

        return False
