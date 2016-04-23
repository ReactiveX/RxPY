import unittest

from rx.testing import TestScheduler, ReactiveTest

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestBufferWithCount(unittest.TestCase):
    def test_buffer_with_count_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(100, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_next(320, 5),
            on_next(350, 6),
            on_next(380, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_completed(600))

        def create():
            return xs.buffer_with_count(3, 2).map(lambda x: str(x))

        results = scheduler.start(create)

        results.messages.assert_equal(
            on_next(280, str([2,3,4])),
            on_next(350, str([4,5,6])),
            on_next(420, str([6,7,8])),
            on_next(600, str([8,9])),
            on_completed(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_buffer_with_count_disposed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(100, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(280, 4),
            on_next(320, 5),
            on_next(350, 6),
            on_next(380, 7),
            on_next(420, 8),
            on_next(470, 9),
            on_completed(600))

        def create():
            return xs.buffer_with_count(3, 2).map(lambda x: str(x))

        results = scheduler.start(create, disposed=370)

        results.messages.assert_equal(on_next(280, str([2, 3, 4])),
        on_next(350, str([4, 5, 6])))
        xs.subscriptions.assert_equal(subscribe(200, 370))


