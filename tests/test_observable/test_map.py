import unittest
from datetime import datetime

from rx.core import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import SerialDisposable

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

class TestSelect(unittest.TestCase):

    def test_select_throws(self):
        with self.assertRaises(RxException):
            Observable.return_value(1) \
                .map_indexed(lambda x, y: x) \
                .subscribe_callbacks(lambda x: _raise("ex"))

        with self.assertRaises(RxException):
            Observable.throw_exception('ex') \
                .map_indexed(lambda x, y: x) \
                .subscribe_callbacks(throw=lambda ex: _raise(ex))

        with self.assertRaises(RxException):
            Observable.empty() \
                .map_indexed(lambda x, y: x) \
                .subscribe_callbacks(lambda x: x, lambda ex: ex, lambda: _raise('ex'))

        def subscribe(observer, scheduler=None):
            _raise('ex')

        with self.assertRaises(RxException):
            Observable.create(subscribe) \
                .map(lambda x: x) \
                .subscribe()

    def test_select_disposeinsideselector(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(100, 1), send(200, 2), send(500, 3), send(600, 4))
        results = scheduler.create_observer()
        d = SerialDisposable()
        invoked = [0]

        def projection(x, *args, **kw):
            invoked[0] += 1

            if scheduler.clock > 400:
                #print("*** Dispose ****")
                d.dispose()
            return x

        d.disposable = xs.map(projection).subscribe(results)

        def action(scheduler, state):
            return d.dispose()

        scheduler.schedule_absolute(ReactiveTest.disposed, action)
        scheduler.start()

        assert results.messages == [send(100, 1), send(200, 2)]
        assert xs.subscriptions == [ReactiveTest.subscribe(0, 500)]

        assert invoked[0] == 3

    def test_select_completed(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(240, 3), send(290, 4), send(350, 5), close(400), send(410, -1), close(420), throw(430, 'ex'))
        invoked = [0]

        def factory():
            def projection(x):
                invoked[0] += 1
                return x + 1

            return xs.map(projection)

        results = scheduler.start(factory)
        assert results.messages == [send(210, 3), send(240, 4), send(290, 5), send(350, 6), close(400)]
        assert xs.subscriptions == [ReactiveTest.subscribe(200, 400)]
        assert invoked[0] == 4


    def test_select_completed_two(self):
        for i in range(100):
            scheduler = TestScheduler()
            invoked = [0]

            xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(240, 3), send(290, 4), send(350, 5), close(400), send(410, -1), close(420), throw(430, 'ex'))
            def factory():
                def projection(x):
                    invoked[0] +=1
                    return x + 1
                return xs.map(projection)

            results = scheduler.start(factory)
            assert results.messages == [send(210, 3), send(240, 4), send(290, 5), send(350, 6), close(400)]
            assert xs.subscriptions == [subscribe(200, 400)]
            assert invoked[0] == 4

    def test_select_not_completed(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(240, 3), send(290, 4), send(350, 5))

        def factory():
            def projection(x):
                invoked[0] += 1
                return x + 1

            return xs.map(projection)

        results = scheduler.start(factory)
        assert results.messages == [send(210, 3), send(240, 4), send(290, 5), send(350, 6)]
        assert xs.subscriptions == [subscribe(200, 1000)]
        assert invoked[0] == 4

    def test_select_error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        invoked = [0]
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(240, 3), send(290, 4), send(350, 5), throw(400, ex), send(410, -1), close(420), throw(430, 'ex'))
        def factory():
            def projection(x):
                invoked[0] += 1
                return x + 1
            return xs.map(projection)

        results = scheduler.start(factory)
        assert results.messages == [send(210, 3), send(240, 4), send(290, 5), send(350, 6), throw(400, ex)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert invoked[0] == 4

    def test_select_selector_throws(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(send(180, 1), send(210, 2), send(240, 3), send(290, 4), send(350, 5), close(400), send(410, -1), close(420), throw(430, 'ex'))

        def factory():
            def projection(x):
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)

                return x + 1
            return xs.map(projection)

        results = scheduler.start(factory)
        assert results.messages == [send(210, 3), send(240, 4), throw(290, ex)]
        assert xs.subscriptions == [subscribe(200, 290)]
        assert invoked[0] == 3

    def test_select_with_index_throws(self):
        with self.assertRaises(RxException):
            return Observable.return_value(1) \
                .map_indexed(lambda x, index: x) \
                .subscribe_callbacks(lambda x: _raise('ex'))

        with self.assertRaises(RxException):
            return Observable.throw_exception('ex') \
                .map_indexed(lambda x, index: x) \
                .subscribe_callbacks(lambda x: x, lambda ex: _raise(ex))

        with self.assertRaises(RxException):
            return Observable.empty() \
                .map(lambda x, index: x) \
                .subscribe_callbacks(lambda x: x, lambda ex: _, lambda : _raise('ex'))

        with self.assertRaises(RxException):
            return Observable.create(lambda o: _raise('ex')) \
                .map_indexed(lambda x, index: x) \
                .subscribe()

    def test_select_with_index_dispose_inside_selector(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(send(100, 4), send(200, 3), send(500, 2), send(600, 1))
        invoked = [0]
        results = scheduler.create_observer()
        d = SerialDisposable()

        def projection(x, index):
            invoked[0] += 1
            if scheduler.clock > 400:
                d.dispose()

            return x + index * 10

        d.disposable = xs.map_indexed(projection).subscribe(results)

        def action(scheduler, state):
            return d.dispose()

        scheduler.schedule_absolute(disposed, action)
        scheduler.start()
        assert results.messages == [send(100, 4), send(200, 13)]
        assert xs.subscriptions == [subscribe(0, 500)]
        assert invoked[0] == 3

    def test_select_with_index_completed(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(send(180, 5), send(210, 4), send(240, 3), send(290, 2), send(350, 1), close(400), send(410, -1), close(420), throw(430, 'ex'))

        def factory():
            def projection(x, index):
                invoked[0] += 1
                return (x + 1) + (index * 10)

            return xs.map_indexed(projection)

        results = scheduler.start(factory)
        assert results.messages == [send(210, 5), send(240, 14), send(290, 23), send(350, 32), close(400)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert invoked[0] == 4

    def test_select_with_index_not_completed(self):
        scheduler = TestScheduler()
        invoked = [0]
        xs = scheduler.create_hot_observable(send(180, 5), send(210, 4), send(240, 3), send(290, 2), send(350, 1))
        def factory():
            def projection(x, index):
                invoked[0] += 1
                return (x + 1) + (index * 10)

            return xs.map_indexed(projection)

        results = scheduler.start(factory)
        assert results.messages == [send(210, 5), send(240, 14), send(290, 23), send(350, 32)]
        assert xs.subscriptions == [subscribe(200, 1000)]
        assert invoked[0] == 4

    def test_select_with_index_error(self):
        scheduler = TestScheduler()
        ex = 'ex'
        invoked = [0]
        xs = scheduler.create_hot_observable(send(180, 5), send(210, 4), send(240, 3), send(290, 2), send(350, 1), throw(400, ex), send(410, -1), close(420), throw(430, 'ex'))

        def factory():
            def projection(x, index):
                invoked[0] += 1
                return (x + 1) + (index * 10)

            return xs.map_indexed(projection)

        results = scheduler.start(factory)

        assert results.messages == [send(210, 5), send(240, 14), send(290, 23), send(350, 32), throw(400, ex)]
        assert xs.subscriptions == [subscribe(200, 400)]
        assert invoked[0] == 4

    def test_select_with_index_selector_throws(self):
        scheduler = TestScheduler()
        invoked = [0]
        ex = 'ex'
        xs = scheduler.create_hot_observable(send(180, 5), send(210, 4), send(240, 3), send(290, 2), send(350, 1), close(400), send(410, -1), close(420), throw(430, 'ex'))

        def factory():
            def projection(x, index):
                invoked[0] += 1
                if invoked[0] == 3:
                    raise Exception(ex)
                return (x + 1) + (index * 10)

            return xs.map_indexed(projection)

        results = scheduler.start(factory)
        assert results.messages == [send(210, 5), send(240, 14), throw(290, ex)]
        assert xs.subscriptions == [subscribe(200, 290)]
        assert invoked[0] == 3

if __name__ == '__main__':
    unittest.main()
