import unittest

from rx.internal import PriorityQueue


class TestItem():
    __test__ = False

    def __init__(self, value, label=None):
        self.value = value
        self.label = label

    def __str__(self):
        if self.label:
            return "%s (%s)" % (self.value, self.label)
        else:
            return "%s" % self.value

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.value == other.value  # and self.label == other.label

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value


class TestPriorityQueue(unittest.TestCase):

    def test_priorityqueue_count(self):
        assert PriorityQueue.MIN_COUNT < 0

    def test_priorityqueue_empty(self):
        """Must be empty on construction"""

        p = PriorityQueue()
        assert len(p) == 0
        assert p.items == []

        # Still empty after enqueue/dequeue
        p.enqueue(42)
        p.dequeue()
        assert len(p) == 0

    def test_priorityqueue_length(self):
        """Test that length is n after n invocations"""

        p = PriorityQueue()

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

    def test_priorityqueue_enqueue_dequeue(self):
        """Enqueue followed by dequeue should give the same result"""

        p = PriorityQueue()
        self.assertRaises(IndexError, p.dequeue)

        p.enqueue(42)
        p.enqueue(41)
        p.enqueue(43)

        assert([p.dequeue(), p.dequeue(), p.dequeue()] == [41, 42, 43])

    def test_priorityqueue_sort_stability(self):
        """Items with same value should be returned in the order they were
        added"""

        p = PriorityQueue()

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

    def test_priorityqueue_remove(self):
        """Remove item from queue"""

        p = PriorityQueue()
        assert(p.remove(42) == False)

        p.enqueue(42)
        p.enqueue(41)
        p.enqueue(43)
        assert p.remove(42) == True
        assert [p.dequeue(), p.dequeue()] == [41, 43]

        p.enqueue(42)
        p.enqueue(41)
        p.enqueue(43)
        assert p.remove(41) == True
        assert [p.dequeue(), p.dequeue()] == [42, 43]

        p.enqueue(42)
        p.enqueue(41)
        p.enqueue(43)
        assert p.remove(43) == True
        assert [p.dequeue(), p.dequeue()] == [41, 42]

    def test_priorityqueue_peek(self):
        """Peek at first element in queue"""

        p = PriorityQueue()

        self.assertRaises(IndexError, p.peek)
        p.enqueue(42)
        assert p.peek() == 42
        p.enqueue(41)
        assert p.peek() == 41
        p.enqueue(43)
        assert p.peek() == 41
