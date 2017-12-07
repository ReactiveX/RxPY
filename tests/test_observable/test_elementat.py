import unittest

from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestElementAt(unittest.TestCase):

    def test_elementat_first(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 42), send(360, 43), send(470, 44), close(600))

        def create():
            return xs.element_at(0)

        results = scheduler.start(create=create)

        results.messages.assert_equal(send(280, 42), close(280))
        xs.subscriptions.assert_equal(subscribe(200, 280))

    def test_elementat_other(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 42), send(360, 43), send(470, 44), close(600))

        def create():
            return xs.element_at(2)

        results = scheduler.start(create=create)

        results.messages.assert_equal(send(470, 44), close(470))
        xs.subscriptions.assert_equal(subscribe(200, 470))

    def test_elementat_outofrange(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 42), send(360, 43), send(470, 44), close(600))

        def create():
            return xs.element_at(3)
        results = scheduler.start(create=create)

        self.assertEqual(1, len(results.messages))
        self.assertEqual(600, results.messages[0].time)
        self.assertEqual('E', results.messages[0].value.kind)
        assert(results.messages[0].value.exception)

    def test_elementat_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 42), send(360, 43), throw(420, ex))

        def create():
            return xs.element_at(3)
        results = scheduler.start(create=create)

        results.messages.assert_equal(throw(420, ex))
        xs.subscriptions.assert_equal(subscribe(200, 420))

    def test_element_at_or_default_first(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 42), send(360, 43), send(470, 44), close(600))

        def create():
            return xs.element_at_or_default(0)
        results = scheduler.start(create=create)

        results.messages.assert_equal(send(280, 42), close(280))
        xs.subscriptions.assert_equal(subscribe(200, 280))

    def test_element_at_or_default_other(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 42), send(360, 43), send(470, 44), close(600))

        def create():
            return xs.element_at_or_default(2)

        results = scheduler.start(create=create)

        results.messages.assert_equal(send(470, 44), close(470))
        xs.subscriptions.assert_equal(subscribe(200, 470))

    def test_element_at_or_default_outofrange(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 42), send(360, 43), send(470, 44), close(600))

        def create():
            return xs.element_at_or_default(3, 0)

        results = scheduler.start(create=create)

        results.messages.assert_equal(send(600, 0), close(600))
        xs.subscriptions.assert_equal(subscribe(200, 600))

    def test_element_at_or_default_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(280, 42), send(360, 43), throw(420, ex))

        def create():
            return xs.element_at_or_default(3)

        results = scheduler.start(create=create)

        results.messages.assert_equal(throw(420, ex))
        xs.subscriptions.assert_equal(subscribe(200, 420))

if __name__ == '__main__':
    unittest.main()
