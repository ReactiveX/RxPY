import unittest

from reactivex.internal import PriorityQueue


class TestItem:
    __test__ = False

    def __init__(self, value: int, label: str | None = None) -> None:
        self.value = value
        self.label = label

    def __str__(self) -> str:
        if self.label:
            return f"{self.value} ({self.label})"
        else:
            return f"{self.value}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TestItem):
            return NotImplemented
        return self.value == other.value  # and self.label == other.label

    def __lt__(self, other: "TestItem") -> bool:
        return self.value < other.value

    def __gt__(self, other: "TestItem") -> bool:
        return self.value > other.value


class TestPriorityQueue(unittest.TestCase):
    def test_priorityqueue_count(self) -> None:
        assert PriorityQueue.MIN_COUNT < 0

    def test_priorityqueue_empty(self) -> None:
        """Must be empty on construction"""

        p: PriorityQueue[int] = PriorityQueue()
        assert len(p) == 0
        assert p.items == []

        # Still empty after enqueue/dequeue
        p.enqueue(42)
        p.dequeue()
        assert len(p) == 0

    def test_priorityqueue_length(self) -> None:
        """Test that length is n after n invocations"""

        p: PriorityQueue[int] = PriorityQueue()

        assert len(p) == 0
        for n in range(42):
            p.enqueue(n)
        assert len(p) == 42
        p.dequeue()
        assert len(p) == 41
        p.remove(10)
        assert len(p) == 40
        for n in range(len(p)):
            p.dequeue()
        assert len(p) == 0

    def test_priorityqueue_enqueue_dequeue(self) -> None:
        """Enqueue followed by dequeue should give the same result"""

        p: PriorityQueue[int] = PriorityQueue()
        self.assertRaises(IndexError, p.dequeue)

        p.enqueue(42)
        p.enqueue(41)
        p.enqueue(43)

        assert [p.dequeue(), p.dequeue(), p.dequeue()] == [41, 42, 43]

    def test_priorityqueue_sort_stability(self) -> None:
        """Items with same value should be returned in the order they were
        added"""

        p: PriorityQueue[TestItem] = PriorityQueue()

        p.enqueue(TestItem(43, "high"))
        p.enqueue(TestItem(42, "first"))
        p.enqueue(TestItem(42, "second"))
        p.enqueue(TestItem(42, "last"))
        p.enqueue(TestItem(41, "low"))

        assert len(p) == 5

        assert p.dequeue() == TestItem(41, "low")
        assert p.dequeue() == TestItem(42, "first")
        assert p.dequeue() == TestItem(42, "second")
        assert p.dequeue() == TestItem(42, "last")
        assert p.dequeue() == TestItem(43, "high")

    def test_priorityqueue_remove(self) -> None:
        """Remove item from queue"""

        p: PriorityQueue[int] = PriorityQueue()
        assert not p.remove(42)

        p.enqueue(42)
        p.enqueue(41)
        p.enqueue(43)
        assert p.remove(42)
        assert [p.dequeue(), p.dequeue()] == [41, 43]

        p.enqueue(42)
        p.enqueue(41)
        p.enqueue(43)
        assert p.remove(41)
        assert [p.dequeue(), p.dequeue()] == [42, 43]

        p.enqueue(42)
        p.enqueue(41)
        p.enqueue(43)
        assert p.remove(43)
        assert [p.dequeue(), p.dequeue()] == [41, 42]

    def test_priorityqueue_peek(self) -> None:
        """Peek at first element in queue"""

        p: PriorityQueue[int] = PriorityQueue()

        self.assertRaises(IndexError, p.peek)
        p.enqueue(42)
        assert p.peek() == 42
        p.enqueue(41)
        assert p.peek() == 41
        p.enqueue(43)
        assert p.peek() == 41
