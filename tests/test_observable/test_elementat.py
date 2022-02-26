import unittest

import rx
from rx import operators as ops
from rx.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestElementAt(unittest.TestCase):

    def test_elementat_first(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))

        def create():
            return xs.pipe(ops.element_at(0))

        results = scheduler.start(create=create)

        assert results.messages == [on_next(280, 42), on_completed(280)]
        assert xs.subscriptions == [subscribe(200, 280)]

    def test_elementat_other(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))

        def create():
            return xs.pipe(ops.element_at(2))

        results = scheduler.start(create=create)

        assert results.messages == [on_next(470, 44), on_completed(470)]
        assert xs.subscriptions == [subscribe(200, 470)]

    def test_elementat_outofrange(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))

        def create():
            return xs.pipe(ops.element_at(3))
        results = scheduler.start(create=create)

        self.assertEqual(1, len(results.messages))
        self.assertEqual(600, results.messages[0].time)
        self.assertEqual('E', results.messages[0].value.kind)
        assert(results.messages[0].value.exception)

    def test_elementat_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_error(420, ex))

        def create():
            return xs.pipe(ops.element_at(3))
        results = scheduler.start(create=create)

        assert results.messages == [on_error(420, ex)]
        assert xs.subscriptions == [subscribe(200, 420)]

    def test_element_at_or_default_first(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))

        def create():
            return xs.pipe(ops.element_at_or_default(0))
        results = scheduler.start(create=create)

        assert results.messages == [on_next(280, 42), on_completed(280)]
        assert xs.subscriptions == [subscribe(200, 280)]

    def test_element_at_or_default_other(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))

        def create():
            return xs.pipe(ops.element_at_or_default(2))

        results = scheduler.start(create=create)

        assert results.messages == [on_next(470, 44), on_completed(470)]
        assert xs.subscriptions == [subscribe(200, 470)]

    def test_element_at_or_default_outofrange(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))

        def create():
            return xs.pipe(ops.element_at_or_default(3, 0))

        results = scheduler.start(create=create)

        assert results.messages == [on_next(600, 0), on_completed(600)]
        assert xs.subscriptions == [subscribe(200, 600)]

    def test_element_at_or_default_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_error(420, ex))

        def create():
            return xs.pipe(ops.element_at_or_default(3))

        results = scheduler.start(create=create)

        assert results.messages == [on_error(420, ex)]
        assert xs.subscriptions == [subscribe(200, 420)]

if __name__ == '__main__':
    unittest.main()
