import logging
import unittest
from datetime import datetime

from rx.testing import TestScheduler, ReactiveTest

FORMAT = '%(asctime)-15s %(threadName)s %(message)s'
logging.basicConfig(filename='rx.log', format=FORMAT, level=logging.DEBUG)
log = logging.getLogger('Rx')

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)


class TestDelay(unittest.TestCase):

    def test_delay_timespan_simple1(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), close(550))

        def create():
            return xs.delay(100)

        results = scheduler.start(create)

        results.messages.assert_equal(send(350, 2), send(450, 3), send(550, 4), close(650))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_datetime_offset_simple1_impl(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), close(550))

        def create():
            dt = datetime.utcfromtimestamp(300/1000.0)
            return xs.delay(dt)

        results = scheduler.start(create)
        results.messages.assert_equal(send(350, 2), send(450, 3), send(550, 4), close(650))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_timespan_simple2_impl(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), close(550))

        def create():
            return xs.delay(50)

        results = scheduler.start(create)
        results.messages.assert_equal(send(300, 2), send(400, 3), send(500, 4), close(600))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_datetime_offset_simple2_impl(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), close(550))

        def create():
            return xs.delay(datetime.utcfromtimestamp(250/1000.0))

        results = scheduler.start(create)

        results.messages.assert_equal(send(300, 2), send(400, 3), send(500, 4), close(600))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_timespan_simple3_impl(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), close(550))

        def create():
            return xs.delay(150)

        results = scheduler.start(create)

        results.messages.assert_equal(send(400, 2), send(500, 3), send(600, 4), close(700))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_datetime_offset_simple3_impl(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), close(550))

        def create():
            return xs.delay(datetime.utcfromtimestamp(0.350))

        results = scheduler.start(create)

        results.messages.assert_equal(send(400, 2), send(500, 3), send(600, 4), close(700))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_timespan_error1_impl(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), throw(550, ex))

        def create():
            return xs.delay(50)

        results = scheduler.start(create)

        results.messages.assert_equal(send(300, 2), send(400, 3), send(500, 4), throw(550, ex))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_datetime_offset_error1_impl(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), throw(550, ex))

        def create():
            return xs.delay(datetime.utcfromtimestamp(0.250))

        results = scheduler.start(create)

        results.messages.assert_equal(send(300, 2), send(400, 3), send(500, 4), throw(550, ex))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_timespan_error2_impl(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), throw(550, ex))

        def create():
            return xs.delay(150)

        results = scheduler.start(create)

        results.messages.assert_equal(send(400, 2), send(500, 3), throw(550, ex))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_datetime_offset_error2_impl(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), send(250, 2), send(350, 3), send(450, 4), throw(550, ex))

        def create():
            return xs.delay(datetime.utcfromtimestamp(0.350))

        results = scheduler.start(create)

        results.messages.assert_equal(send(400, 2), send(500, 3), throw(550, ex))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), close(550))

        def create():
            return xs.delay(10)

        results = scheduler.start(create)

        results.messages.assert_equal(close(560))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1), throw(550, ex))

        def create():
            return xs.delay(10)

        results = scheduler.start(create)

        results.messages.assert_equal(throw(550, ex))
        xs.subscriptions.assert_equal(subscribe(200, 550))

    def test_delay_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(150, 1))

        def create():
            return xs.delay(10)

        results = scheduler.start(create)

        results.messages.assert_equal()
        xs.subscriptions.assert_equal(subscribe(200, 1000))
