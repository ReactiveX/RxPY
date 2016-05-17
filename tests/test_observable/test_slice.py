import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestSlice(unittest.TestCase):

    def test_slice_empty(self):
        scheduler = TestScheduler()
        msgs = [on_next(150, 1), on_completed(250)]
        xs = scheduler.create_hot_observable(msgs)

        def create():
            return xs[1:42]

        res = scheduler.start(create=create).messages
        res.assert_equal(on_completed(250))

    def test_slice_same(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, -2),
            on_next(150, -1),
            on_next(210, 0),
            on_next(230, 1),
            on_next(270, 2),
            on_next(280, 3),
            on_next(300, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(370, 7),
            on_next(410, 8),
            on_next(415, 9),
            on_completed(690))

        def create():
            return xs[0:10]
        results = scheduler.start(create)
        results.messages.assert_equal(
            on_next(210, 0),
            on_next(230, 1),
            on_next(270, 2),
            on_next(280, 3),
            on_next(300, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(370, 7),
            on_next(410, 8),
            on_next(415, 9),
            on_completed(415))
        xs.subscriptions.assert_equal(subscribe(200, 415))

    def test_slice_same_noop(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, -2),
            on_next(150, -1),
            on_next(210, 0),
            on_next(230, 1),
            on_next(270, 2),
            on_next(280, 3),
            on_next(300, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(370, 7),
            on_next(410, 8),
            on_next(415, 9),
            on_completed(690))

        def create():
            return xs[:]
        results = scheduler.start(create)
        results.messages.assert_equal(
            on_next(210, 0),
            on_next(230, 1),
            on_next(270, 2),
            on_next(280, 3),
            on_next(300, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(370, 7),
            on_next(410, 8),
            on_next(415, 9),
            on_completed(690))
        xs.subscriptions.assert_equal(subscribe(200, 1000))

    def test_slice_skip_first(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, -2),
            on_next(150, -1),
            on_next(210, 0),
            on_next(230, 1),
            on_next(270, 2),
            on_next(280, 3),
            on_next(300, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(370, 7),
            on_next(410, 8),
            on_next(415, 9),
            on_completed(690))

        def create():
            return xs[2:]
        results = scheduler.start(create)
        results.messages.assert_equal(
            on_next(270, 2),
            on_next(280, 3),
            on_next(300, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(370, 7),
            on_next(410, 8),
            on_next(415, 9),
            on_completed(690))
        xs.subscriptions.assert_equal(subscribe(200, 690))

    def test_slice_skip_last(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, -2),
            on_next(150, -1),
            on_next(210, 0),
            on_next(230, 1),
            on_next(270, 2),
            on_next(280, 3),
            on_next(300, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(370, 7),
            on_next(410, 8),
            on_next(415, 9),
            on_completed(690))

        def create():
            return xs[:-2]
        results = scheduler.start(create)
        results.messages.assert_equal(
            on_next(270, 0),
            on_next(280, 1),
            on_next(300, 2),
            on_next(310, 3),
            on_next(340, 4),
            on_next(370, 5),
            on_next(410, 6),
            on_next(415, 7),
            on_completed(690))
        xs.subscriptions.assert_equal(subscribe(200, 690))

    def test_slice_take_last(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, -2),
            on_next(150, -1),
            on_next(210, 0),
            on_next(230, 1),
            on_next(270, 2),
            on_next(280, 3),
            on_next(300, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(370, 7),
            on_next(410, 8),
            on_next(415, 9),
            on_completed(690))

        def create():
            return xs[-2:]
        results = scheduler.start(create)
        results.messages.assert_equal(
            on_next(690, 8),
            on_next(690, 9),
            on_completed(690))
        xs.subscriptions.assert_equal(subscribe(200, 690))

    def test_slice_take_first(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, -2),
            on_next(150, -1),
            on_next(210, 0),
            on_next(230, 1),
            on_next(270, 2),
            on_next(280, 3),
            on_next(300, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(370, 7),
            on_next(410, 8),
            on_next(415, 9),
            on_completed(690))

        def create():
            return xs[:2]
        results = scheduler.start(create)
        results.messages.assert_equal(
            on_next(210, 0),
            on_next(230, 1),
            on_completed(230))
        xs.subscriptions.assert_equal(subscribe(200, 230))

    def test_slice_step_2(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(70, -2),
            on_next(150, -1),
            on_next(210, 0),
            on_next(230, 1),
            on_next(270, 2),
            on_next(280, 3),
            on_next(300, 4),
            on_next(310, 5),
            on_next(340, 6),
            on_next(370, 7),
            on_next(410, 8),
            on_next(415, 9),
            on_completed(690))

        def create():
            return xs[0:10:2]
        results = scheduler.start(create)
        results.messages.assert_equal(
            on_next(210, 0),
            on_next(270, 2),
            on_next(300, 4),
            on_next(340, 6),
            on_next(410, 8),
            on_completed(415))
        xs.subscriptions.assert_equal(subscribe(200, 415))
