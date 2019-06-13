import unittest

from rx import return_value, throw, empty, create
from rx.testing import TestScheduler, ReactiveTest
from rx.disposable import SerialDisposable

from rx import operators as ops

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass

# Helper function for raising exceptions within lambdas


def _raise(ex):
    raise RxException(ex)


class TestSelect(unittest.TestCase):

    def test_starmap_never(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable()

        invoked = [0]

        def factory():
            def mapper(x, y):
                invoked[0] += 1
                return x + y

            return xs.pipe(ops.starmap(mapper))

        results = scheduler.start(factory)
        assert results.messages == []
        assert xs.subscriptions == [ReactiveTest.subscribe(200, 1000)]
        assert invoked[0] == 0

    def test_starmap_empty(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            # 100 create
            # 200 subscribe
            on_completed(300),
            )

        invoked = [0]

        def factory():
            def mapper(x, y):
                invoked[0] += 1
                return x + y

            return xs.pipe(ops.starmap(mapper))

        results = scheduler.start(factory)
        assert results.messages == [on_completed(300)]
        assert xs.subscriptions == [ReactiveTest.subscribe(200, 300)]
        assert invoked[0] == 0

    def test_starmap_subscription_error(self):
        mapper = ops.starmap(lambda x, y: (x, y))

        with self.assertRaises(RxException):
            return_value((1, 10)).pipe(
                mapper
            ).subscribe(lambda x: _raise("ex"))

        with self.assertRaises(RxException):
            throw('ex').pipe(
                mapper
            ).subscribe(on_error=lambda ex: _raise(ex))

        with self.assertRaises(RxException):
            empty().pipe(
                mapper
            ).subscribe(lambda x: x, lambda ex: ex, lambda: _raise('ex'))

        def subscribe(observer, scheduler=None):
            _raise('ex')

        with self.assertRaises(RxException):
            create(subscribe_observer=subscribe).pipe(
                mapper
            ).subscribe()

    def test_starmap_dispose_inside_mapper(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            # 100 create
            on_next(110, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(310, (3, 30)),
            on_next(410, (4, 40)))

        results = scheduler.create_observer()
        d = SerialDisposable()
        invoked = [0]

        def mapper(x, y):
            invoked[0] += 1
            if scheduler._clock > 250:
                d.dispose()
            return x + y

        d.disposable = xs.pipe(
            ops.starmap(mapper)
        ).subscribe_observer(results, scheduler=scheduler)

        def action(scheduler, state):
            return d.dispose()

        scheduler.schedule_absolute(ReactiveTest.disposed, action)
        scheduler.start()

        assert results.messages == [
                on_next(110, 11),
                on_next(210, 22)]

        assert xs.subscriptions == [ReactiveTest.subscribe(0, 310)]
        assert invoked[0] == 3

    def test_starmap_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_completed(400),
            on_next(410, (-1, -10)),
            on_completed(420),
            on_error(430, 'ex'))

        invoked = [0]

        def factory():
            def mapper(x, y):
                invoked[0] += 1
                return x + y

            return xs.pipe(ops.starmap(mapper))

        results = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 22),
            on_next(240, 33),
            on_next(290, 44),
            on_next(350, 55),
            on_completed(400)]

        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_not_completed(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)))

        def factory():
            def mapper(x, y):
                invoked[0] += 1
                return x + y

            return xs.pipe(ops.starmap(mapper))

        results = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 22),
            on_next(240, 33),
            on_next(290, 44),
            on_next(350, 55)]

        assert xs.subscriptions == [subscribe(200, 1000)]
        assert invoked[0] == 4

    def test_starmap_no_mapper(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_completed(400),
            on_next(410, (-1, -10)),
            on_completed(420),
            on_error(430, 'ex'))

        def factory():
            return xs.pipe(ops.starmap())

        results = scheduler.start(factory)
        assert results.messages == [
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_completed(400)]

        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]


    def test_starmap_mapper_with_one_element(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1,)),
            # 200 subscribe
            on_next(210, (2,)),
            on_next(240, (3,)),
            on_next(290, (4,)),
            on_next(350, (5,)),
            on_completed(400),
            on_next(410, (-1,)),
            on_completed(420),
            on_error(430, 'ex'))

        invoked = [0]

        def factory():
            def mapper(x):
                invoked[0] += 1
                return x * 10

            return xs.pipe(ops.starmap(mapper))

        results = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 20),
            on_next(240, 30),
            on_next(290, 40),
            on_next(350, 50),
            on_completed(400)]

        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_mapper_with_three_elements(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10, 100)),
            # 200 subscribe
            on_next(210, (2, 20, 200)),
            on_next(240, (3, 30, 300)),
            on_next(290, (4, 40, 400)),
            on_next(350, (5, 50, 500)),
            on_completed(400),
            on_next(410, (-1, -10, -100)),
            on_completed(420),
            on_error(430, 'ex'))

        invoked = [0]

        def factory():
            def mapper(x, y, z):
                invoked[0] += 1
                return x + y + z

            return xs.pipe(ops.starmap(mapper))

        results = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 222),
            on_next(240, 333),
            on_next(290, 444),
            on_next(350, 555),
            on_completed(400)]

        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_mapper_with_args(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_completed(400),
            on_next(410, (-1, -10)),
            on_completed(420),
            on_error(430, 'ex'))

        invoked = [0]

        def factory():
            def mapper(*args):
                invoked[0] += 1
                return sum(args)

            return xs.pipe(ops.starmap(mapper))

        results = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 22),
            on_next(240, 33),
            on_next(290, 44),
            on_next(350, 55),
            on_completed(400)]

        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        invoked = [0]
        xs = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_error(400, ex),
            on_next(410, (-1, -10)),
            on_completed(420),
            on_error(430, ex))

        def factory():
            def mapper(x, y):
                invoked[0] += 1
                return x + y
            return xs.pipe(ops.starmap(mapper))

        results = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 22),
            on_next(240, 33),
            on_next(290, 44),
            on_next(350, 55),
            on_error(400, ex)]

        assert xs.subscriptions == [subscribe(200, 400)]
        assert invoked[0] == 4

    def test_starmap_mapper_error(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(
            # 100 create
            on_next(180, (1, 10)),
            # 200 subscribe
            on_next(210, (2, 20)),
            on_next(240, (3, 30)),
            on_next(290, (4, 40)),
            on_next(350, (5, 50)),
            on_completed(400),
            on_next(410, (-1, -10)),
            on_completed(420),
            on_error(430, ex))

        def factory():
            def mapper(x, y):
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)

                return x + y
            return xs.pipe(ops.starmap(mapper))

        results = scheduler.start(factory)
        assert results.messages == [
            on_next(210, 22),
            on_next(240, 33),
            on_error(290, ex)]

        assert xs.subscriptions == [subscribe(200, 290)]
        assert invoked[0] == 3


if __name__ == '__main__':
    unittest.main()
