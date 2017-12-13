import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSlice(unittest.TestCase):

    def test_slice_empty(self):
        scheduler = TestScheduler()
        msgs = [send(150, 1), close(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs[1:42]

        res = scheduler.start(create=create).messages
        assert res == [close(250)]

    def test_slice_same(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(70, -2),
            send(150, -1),
            send(210, 0),
            send(230, 1),
            send(270, 2),
            send(280, 3),
            send(300, 4),
            send(310, 5),
            send(340, 6),
            send(370, 7),
            send(410, 8),
            send(415, 9),
            close(690))

        def create():
            return xs[0:10]
        results = scheduler.start(create)
        assert results.messages == [
            send(210, 0),
            send(230, 1),
            send(270, 2),
            send(280, 3),
            send(300, 4),
            send(310, 5),
            send(340, 6),
            send(370, 7),
            send(410, 8),
            send(415, 9),
            close(415)]
        assert xs.subscriptions == [subscribe(200, 415)]

    def test_slice_same_noop(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(70, -2),
            send(150, -1),
            send(210, 0),
            send(230, 1),
            send(270, 2),
            send(280, 3),
            send(300, 4),
            send(310, 5),
            send(340, 6),
            send(370, 7),
            send(410, 8),
            send(415, 9),
            close(690))

        def create():
            return xs[:]
        results = scheduler.start(create)
        assert results.messages == [
            send(210, 0),
            send(230, 1),
            send(270, 2),
            send(280, 3),
            send(300, 4),
            send(310, 5),
            send(340, 6),
            send(370, 7),
            send(410, 8),
            send(415, 9),
            close(690)]
        assert xs.subscriptions == [subscribe(200, 1000)]

    def test_slice_skip_first(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(70, -2),
            send(150, -1),
            send(210, 0),
            send(230, 1),
            send(270, 2),
            send(280, 3),
            send(300, 4),
            send(310, 5),
            send(340, 6),
            send(370, 7),
            send(410, 8),
            send(415, 9),
            close(690))

        def create():
            return xs[2:]
        results = scheduler.start(create)
        assert results.messages == [
            send(270, 2),
            send(280, 3),
            send(300, 4),
            send(310, 5),
            send(340, 6),
            send(370, 7),
            send(410, 8),
            send(415, 9),
            close(690)]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_slice_skip_last(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(70, -2),
            send(150, -1),
            send(210, 0),
            send(230, 1),
            send(270, 2),
            send(280, 3),
            send(300, 4),
            send(310, 5),
            send(340, 6),
            send(370, 7),
            send(410, 8),
            send(415, 9),
            close(690))

        def create():
            return xs[:-2]
        results = scheduler.start(create)
        assert results.messages == [
            send(270, 0),
            send(280, 1),
            send(300, 2),
            send(310, 3),
            send(340, 4),
            send(370, 5),
            send(410, 6),
            send(415, 7),
            close(690)]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_slice_take_last(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(70, -2),
            send(150, -1),
            send(210, 0),
            send(230, 1),
            send(270, 2),
            send(280, 3),
            send(300, 4),
            send(310, 5),
            send(340, 6),
            send(370, 7),
            send(410, 8),
            send(415, 9),
            close(690))

        def create():
            return xs[-2:]
        results = scheduler.start(create)
        assert results.messages == [
            send(690, 8),
            send(690, 9),
            close(690)]
        assert xs.subscriptions == [subscribe(200, 690)]

    def test_slice_take_first(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(70, -2),
            send(150, -1),
            send(210, 0),
            send(230, 1),
            send(270, 2),
            send(280, 3),
            send(300, 4),
            send(310, 5),
            send(340, 6),
            send(370, 7),
            send(410, 8),
            send(415, 9),
            close(690))

        def create():
            return xs[:2]
        results = scheduler.start(create)
        assert results.messages == [
            send(210, 0),
            send(230, 1),
            close(230)]
        assert xs.subscriptions == [subscribe(200, 230)]

    def test_slice_step_2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            send(70, -2),
            send(150, -1),
            send(210, 0),
            send(230, 1),
            send(270, 2),
            send(280, 3),
            send(300, 4),
            send(310, 5),
            send(340, 6),
            send(370, 7),
            send(410, 8),
            send(415, 9),
            close(690))

        def create():
            return xs[0:10:2]
        results = scheduler.start(create)
        assert results.messages == [
            send(210, 0),
            send(270, 2),
            send(300, 4),
            send(340, 6),
            send(410, 8),
            close(415)]
        assert xs.subscriptions == [subscribe(200, 415)]
