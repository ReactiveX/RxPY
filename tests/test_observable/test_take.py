import unittest

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestTake(unittest.TestCase):

    def test_take_complete_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 6), send(150, 4), send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10), close(690))

        def create():
            return xs.take(20)
        results = scheduler.start(create)
        assert results.messages == [send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10), close(690)]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_take_complete_same(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 6), send(150, 4), send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10), close(690))

        def create():
            return xs.take(17)
        results = scheduler.start(create)
        assert results.messages == [send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10), close(630)]
        assert xs.subscriptions == [subscribe(200, 630)]

    def test_take_complete_before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 6), send(150, 4), send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10), close(690))

        def create():
            return xs.take(10)
        results = scheduler.start(create)

        assert results.messages == [send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), close(415)]
        assert xs.subscriptions == [subscribe(200, 415)]

    def test_take_error_after(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 6), send(150, 4), send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10), throw(690, ex))

        def create():
            return xs.take(20)
        results = scheduler.start(create)

        assert results.messages == [send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10), throw(690, ex)]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_take_error_same(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 6), send(150, 4), send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10), throw(690, 'ex'))

        def create():
            return xs.take(17)
        results = scheduler.start(create)

        assert results.messages == [send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10), close(630)]
        assert xs.subscriptions == [subscribe(200, 630)]


    def test_take_error_before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 6), send(150, 4), send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10), throw(690, 'ex'))

        def create():
            return xs.take(3)
        results = scheduler.start(create)

        assert results.messages == [send(210, 9), send(230, 13), send(270, 7), close(270)]
        assert xs.subscriptions == [subscribe(200, 270)]

    def test_take_dispose_before(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 6), send(150, 4), send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10))

        def create():
            return xs.take(3)
        results = scheduler.start(create, disposed=250)
        assert results.messages == [send(210, 9), send(230, 13)]
        assert xs.subscriptions == [subscribe(200, 250)]

    def test_take_dispose_after(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(70, 6), send(150, 4), send(210, 9), send(230, 13), send(270, 7), send(280, 1), send(300, -1), send(310, 3), send(340, 8), send(370, 11), send(410, 15), send(415, 16), send(460, 72), send(510, 76), send(560, 32), send(570, -100), send(580, -3), send(590, 5), send(630, 10))

        def create():
            return xs.take(3)
        results = scheduler.start(create, disposed=400)
        assert results.messages == [send(210, 9), send(230, 13), send(270, 7), close(270)]
        assert xs.subscriptions == [subscribe(200, 270)]
