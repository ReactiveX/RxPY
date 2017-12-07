import unittest
from nose import SkipTest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

try:
    from transducer.functional import compose
    from transducer.react import transduce
    from transducer.transducers import (mapping, filtering, reducing)
except ImportError:
    raise SkipTest("Transducers not available")

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


def even(x):
    return x % 2 == 0


def mul10(x):
    return x * 10


def noop(*args):
    pass


def identity(x):
    return x


def throw_error(*args):
    print("throwing...")
    raise RxException()


class RxException(Exception):
    pass


class TestTransduce(unittest.TestCase):

    def test_transduce_raises(self):
        def create():
            Observable.throw_exception(RxException()).transduce(
                compose(
                    filtering(even), mapping(mul10))
                ).subscribe_callbacks(noop, throw_error)

        self.assertRaises(RxException, create)

        def create2():
            Observable.empty().transduce(
                compose(
                    filtering(even), mapping(mul10))
                ).subscribe_callbacks(noop, noop, throw_error)

        self.assertRaises(RxException, create2)

        def create3():
            Observable.create(throw_error).transduce(
                compose(
                    filtering(even), mapping(mul10))
                ).subscribe()

            self.assertRaises(RxException, create3)

    def test_transduce_never(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(150, 1)
        )

        def create():
            return xs.transduce(compose(filtering(even), mapping(mul10)))

        results = scheduler.start(create)

        results.messages.assert_equal()

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )

    def test_transduce_empty(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            close(250)
        )

        def create():
            return xs.transduce(compose(filtering(even), mapping(mul10)))

        results = scheduler.start(create)

        results.messages.assert_equal(
            close(250)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 250)
        )

    def test_transduce_some(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(220, 3),
            send(230, 4),
            send(240, 5),
            close(250)
        )

        i = [0]

        def even_filter(x):
            i[0] += 1
            return x % 2 == 0

        def create():
            return xs.transduce(
                compose(filtering(even_filter), mapping(mul10))
            )

        results = scheduler.start(create)

        results.messages.assert_equal(
            send(210, 20),
            send(230, 40),
            close(250)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 250)
        )

        self.assertEqual(4, i[0])

    def test_transduce_ifinite(self):
        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(220, 3),
            send(230, 4),
            send(240, 5)
        )

        i = [0]

        def even_filter(x):
            i[0] += 1
            return x % 2 == 0

        def create():
            return xs.transduce(
                compose(filtering(even_filter), mapping(mul10))
            )

        results = scheduler.start(create)

        results.messages.assert_equal(
            send(210, 20),
            send(230, 40)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 1000)
        )

        self.assertEqual(4, i[0])

    def test_transduce_error(self):
        error = RxException()

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            throw(210, error)
        )

        def create():
            return xs.transduce(compose(filtering(even), mapping(mul10)))

        results = scheduler.start(create)

        results.messages.assert_equal(
            throw(210, error)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 210)
        )

    def test_transduce_throw(self):
        error = RxException()

        scheduler = TestScheduler()

        xs = scheduler.create_hot_observable(
            send(150, 1),
            send(210, 2),
            send(220, 3),
            send(230, 4),
            send(240, 5),
            close(250)
        )

        i = [0]

        def even_filter(x):
            if i[0] > 2:
                raise error
            else:
                i[0] += 1
                return x % 2 == 0

        def create():
            return xs.transduce(
                compose(filtering(even_filter), mapping(mul10))
            )

        results = scheduler.start(create)

        results.messages.assert_equal(
            send(210, 20),
            send(230, 40),
            throw(240, error)
        )

        xs.subscriptions.assert_equal(
            subscribe(200, 240)
        )
