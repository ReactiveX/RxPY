import unittest

from rx.testing import TestScheduler, ReactiveTest


class TestToArray(ReactiveTest, unittest.TestCase):

    def test_toiterable_completed(self):
        scheduler = TestScheduler()
        msgs = [
            self.send(110, 1),
            self.send(220, 2),
            self.send(330, 3),
            self.send(440, 4),
            self.send(550, 5),
            self.close(660)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.to_iterable()
        results = scheduler.start(create=create).messages

        assert len(results) == 2
        assert results[0].time == 660
        assert results[0].value.kind == 'N'
        assert results[0].value.value == [2, 3, 4, 5]
        assert self.close(660).equals(results[1])
        assert xs.subscriptions == [self.subscribe(200, 660)]

    def test_toiterableerror(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs = [
            self.send(110, 1),
            self.send(220, 2),
            self.send(330, 3),
            self.send(440, 4),
            self.send(550, 5),
            self.throw(660, ex)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.to_iterable()
        results = scheduler.start(create=create).messages
        assert results == [self.throw(660, ex)]
        assert xs.subscriptions == [self.subscribe(200, 660)]

    def test_toiterabledisposed(self):
        scheduler = TestScheduler()
        msgs = [
            self.send(110, 1),
            self.send(220, 2),
            self.send(330, 3),
            self.send(440, 4),
            self.send(550, 5)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs.to_iterable()

        results = scheduler.start(create=create).messages
        assert results == []
        assert xs.subscriptions == [self.subscribe(200, 1000)]
