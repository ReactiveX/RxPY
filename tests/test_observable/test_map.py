import unittest

from rx import Observable, return_value, throw, empty, create
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import SerialDisposable

from rx.operators import map, map_indexed

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

    def test_map_throws(self):
        mapper = map_indexed(lambda x, y: x)
        with self.assertRaises(RxException):
            return_value(1).pipe(
                mapper
            ).subscribe_(lambda x: _raise("ex"))

        with self.assertRaises(RxException):
            throw('ex').pipe(
                mapper
            ).subscribe_(on_error=lambda ex: _raise(ex))

        with self.assertRaises(RxException):
            empty().pipe(
                mapper
            ).subscribe_(lambda x: x, lambda ex: ex, lambda: _raise('ex'))

        def subscribe(observer, scheduler=None):
            _raise('ex')

        with self.assertRaises(RxException):
            create(subscribe).pipe(
                map(lambda x: x)
            ).subscribe()

    def test_map_disposeinsidemapper(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 1), on_next(200, 2), on_next(500, 3), on_next(600, 4))
        results = scheduler.create_observer()
        d = SerialDisposable()
        invoked = [0]

        def projection(x, *args, **kw):
            invoked[0] += 1

            if scheduler.clock > 400:
                d.dispose()
            return x

        d.disposable = xs.pipe(
            map(projection)
        ).subscribe(results, scheduler)

        def action(scheduler, state):
            return d.dispose()

        scheduler.schedule_absolute(ReactiveTest.disposed, action)
        scheduler.start()

        assert results.messages == [on_next(100, 1), on_next(200, 2)]
        assert xs.subscriptions == [ReactiveTest.subscribe(0, 500)]

        assert invoked[0] == 3

    def test_map_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(
            on_next(180, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(290, 4),
            on_next(350, 5),
            on_completed(400),
            on_next(410, -1),
            on_completed(420),
            on_error(430, 'ex'))
        invoked = [0]

        def factory():
            def projection(x):
                invoked[0] += 1
                return x + 1

            return xs.pipe(map(projection))

        results = scheduler.start(factory)
        assert results.messages == [on_next(210, 3), on_next(
            240, 4), on_next(290, 5), on_next(350, 6), on_completed(400)]
        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4

    def test_map_completed_two(self):
        for i in range(100):
            scheduler = TestScheduler()
            invoked = [0]

            xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(240, 3), on_next(
                290, 4), on_next(350, 5), on_completed(400), on_next(410, -1), on_completed(420), on_error(430, 'ex'))

            def factory():
                def projection(x):
                    invoked[0] += 1
                    return x + 1
                return xs.pipe(map(projection))

            results = scheduler.start(factory)
            assert results.messages == [on_next(210, 3), on_next(
                240, 4), on_next(290, 5), on_next(350, 6), on_completed(400)]
            assert xs.subscriptions == [subscribe(200, 400)]
            assert invoked[0] == 4

    def test_map_not_completed(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(
            210, 2), on_next(240, 3), on_next(290, 4), on_next(350, 5))

        def factory():
            def projection(x):
                invoked[0] += 1
                return x + 1

            return xs.pipe(map(projection))

        results = scheduler.start(factory)
        assert results.messages == [on_next(210, 3), on_next(240, 4), on_next(290, 5), on_next(350, 6)]
        assert xs.subscriptions == [subscribe(200, 1000)]
        assert invoked[0] == 4

    def test_map_error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(240, 3), on_next(
            290, 4), on_next(350, 5), on_error(400, ex), on_next(410, -1), on_completed(420), on_error(430, 'ex'))

        def factory():
            def projection(x):
                invoked[0] += 1
                return x + 1
            return xs.pipe(map(projection))

        results = scheduler.start(factory)
        assert results.messages == [on_next(210, 3), on_next(
            240, 4), on_next(290, 5), on_next(350, 6), on_error(400, ex)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert invoked[0] == 4

    def test_map_mapper_throws(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(
            on_next(180, 1),
            on_next(210, 2),
            on_next(240, 3),
            on_next(290, 4),
            on_next(350, 5),
            on_completed(400),
            on_next(410, -1),
            on_completed(420),
            on_error(430, 'ex'))

        def factory():
            def projection(x):
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)

                return x + 1
            return xs.pipe(map(projection))

        results = scheduler.start(factory)
        assert results.messages == [on_next(210, 3), on_next(240, 4), on_error(290, ex)]
        assert xs.subscriptions == [subscribe(200, 290)]
        assert invoked[0] == 3

    def test_map_with_index_throws(self):
        with self.assertRaises(RxException):
            mapper = map_indexed(lambda x, index: x)

            return return_value(1).pipe(
                mapper
            ).subscribe_(lambda x: _raise('ex'))

        with self.assertRaises(RxException):
            return throw('ex').pipe(
                mapper
            ).subscribe_(lambda x: x, lambda ex: _raise(ex))

        with self.assertRaises(RxException):
            return empty().pipe(
                mapper
            ).subscribe_(lambda x: x, lambda ex: None, lambda: _raise('ex'))

        with self.assertRaises(RxException):
            return create(lambda o, s: _raise('ex')).pipe(
                mapper
            ).subscribe()

    def test_map_with_index_dispose_inside_mapper(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(100, 4), on_next(200, 3), on_next(500, 2), on_next(600, 1))
        invoked = [0]
        results = scheduler.create_observer()
        d = SerialDisposable()

        def projection(x, index):
            invoked[0] += 1
            if scheduler.clock > 400:
                d.dispose()

            return x + index * 10

        d.disposable = xs.pipe(map_indexed(projection)).subscribe(results)

        def action(scheduler, state):
            return d.dispose()

        scheduler.schedule_absolute(disposed, action)
        scheduler.start()
        assert results.messages == [on_next(100, 4), on_next(200, 13)]
        assert xs.subscriptions == [subscribe(0, 500)]
        assert invoked[0] == 3

    def test_map_with_index_completed(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(180, 5), on_next(210, 4), on_next(240, 3), on_next(
            290, 2), on_next(350, 1), on_completed(400), on_next(410, -1), on_completed(420), on_error(430, 'ex'))

        def factory():
            def projection(x, index):
                invoked[0] += 1
                return (x + 1) + (index * 10)

            return xs.pipe(map_indexed(projection))

        results = scheduler.start(factory)
        assert results.messages == [on_next(210, 5), on_next(
            240, 14), on_next(290, 23), on_next(350, 32), on_completed(400)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert invoked[0] == 4

    def test_map_with_index_not_completed(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(180, 5), on_next(
            210, 4), on_next(240, 3), on_next(290, 2), on_next(350, 1))

        def factory():
            def projection(x, index):
                invoked[0] += 1
                return (x + 1) + (index * 10)

            return xs.pipe(map_indexed(projection))

        results = scheduler.start(factory)
        assert results.messages == [on_next(210, 5), on_next(240, 14), on_next(290, 23), on_next(350, 32)]
        assert xs.subscriptions == [subscribe(200, 1000)]
        assert invoked[0] == 4

    def test_map_with_index_error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        invoked = [0]
        xs = scheduler.create_hot_observable(on_next(180, 5), on_next(210, 4), on_next(240, 3), on_next(
            290, 2), on_next(350, 1), on_error(400, ex), on_next(410, -1), on_completed(420), on_error(430, 'ex'))

        def factory():
            def projection(x, index):
                invoked[0] += 1
                return (x + 1) + (index * 10)

            return xs.pipe(map_indexed(projection))

        results = scheduler.start(factory)

        assert results.messages == [on_next(210, 5), on_next(
            240, 14), on_next(290, 23), on_next(350, 32), on_error(400, ex)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert invoked[0] == 4

    def test_map_with_index_mapper_throws(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(on_next(180, 5), on_next(210, 4), on_next(240, 3), on_next(
            290, 2), on_next(350, 1), on_completed(400), on_next(410, -1), on_completed(420), on_error(430, 'ex'))

        def factory():
            def projection(x, index):
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)
                return (x + 1) + (index * 10)

            return xs.pipe(map_indexed(projection))

        results = scheduler.start(factory)
        assert results.messages == [on_next(210, 5), on_next(240, 14), on_error(290, ex)]
        assert xs.subscriptions == [subscribe(200, 290)]
        assert invoked[0] == 3


if __name__ == '__main__':
    unittest.main()
