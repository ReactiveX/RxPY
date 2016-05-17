import unittest

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest, MockDisposable

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


class TestUsing(unittest.TestCase):
    def test_using_null(self):
        disposable = [None]
        xs = [None]
        _d = [None]

        scheduler = TestScheduler()
        dispose_invoked = [0]
        create_invoked = [0]

        def create():
            def create_resources():
                dispose_invoked[0] += 1
                disposable[0] = None
                return disposable[0]

            def create_observable(d):
                _d[0] = d
                create_invoked[0] += 1
                xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_completed(200))
                return xs[0]
            return Observable.using(create_resources, create_observable)

        results = scheduler.start(create)

        assert(disposable[0] == _d[0])
        results.messages.assert_equal(on_next(300, 200), on_completed(400))
        assert(1 == create_invoked[0])
        assert(1 == dispose_invoked[0])
        xs[0].subscriptions.assert_equal(subscribe(200, 400))
        assert(disposable[0] == None)

    def test_using_complete(self):
        disposable = [None]
        xs = [None]
        _d = [None]
        scheduler = TestScheduler()
        dispose_invoked = [0]
        create_invoked = [0]

        def create():
            def create_resource():
                dispose_invoked[0] += 1
                disposable[0] = MockDisposable(scheduler)
                return disposable[0]
            def create_observable(d):
                _d[0] = d
                create_invoked[0] += 1
                xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_completed(200))
                return xs[0]
            return Observable.using(create_resource, create_observable)

        results = scheduler.start(create)

        assert(disposable == _d)
        results.messages.assert_equal(on_next(300, 200), on_completed(400))
        assert(create_invoked[0] == 1)
        assert(dispose_invoked[0] == 1)
        xs[0].subscriptions.assert_equal(subscribe(200, 400))
        disposable[0].disposes.assert_equal(200, 400)

    def test_using_error(self):
        scheduler = TestScheduler()
        dispose_invoked = [0]
        create_invoked = [0]
        ex = 'ex'
        disposable = [None]
        xs = [None]
        _d = [None]

        def create():
            def create_resource():
                dispose_invoked[0] += 1
                disposable[0] = MockDisposable(scheduler)
                return disposable[0]
            def create_observable(d):
                _d[0] = d
                create_invoked[0] += 1
                xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_error(200, ex))
                return xs[0]
            return Observable.using(create_resource, create_observable)
        results = scheduler.start(create)

        assert (disposable[0] == _d[0])
        results.messages.assert_equal(on_next(300, 200), on_error(400, ex))
        assert(create_invoked[0] == 1)
        assert(dispose_invoked[0] == 1)
        xs[0].subscriptions.assert_equal(subscribe(200, 400))
        disposable[0].disposes.assert_equal(200, 400)

    def test_using_dispose(self):
        disposable = [None]
        xs = [None]
        _d = [None]
        scheduler = TestScheduler()
        dispose_invoked = [0]
        create_invoked = [0]

        def create():
            def create_resource():
                dispose_invoked[0] += 1
                disposable[0] = MockDisposable(scheduler)
                return disposable[0]
            def create_observable(d):
                _d[0] = d
                create_invoked[0] += 1
                xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_next(1000, scheduler.clock + 1))
                return xs[0]
            return Observable.using(create_resource, create_observable)
        results = scheduler.start(create)

        assert(disposable[0] == _d[0])
        results.messages.assert_equal(on_next(300, 200))
        assert(1 == create_invoked[0])
        assert(1 == dispose_invoked[0])
        xs[0].subscriptions.assert_equal(subscribe(200, 1000))
        disposable[0].disposes.assert_equal(200, 1000)

    def test_using_throw_resource_selector(self):
        scheduler = TestScheduler()
        dispose_invoked = [0]
        create_invoked = [0]
        ex = 'ex'

        def create():
            def create_resource():
                dispose_invoked[0] += 1
                raise _raise(ex)
            def create_observable(d):
                create_invoked[0] += 1
                return Observable.never()

            return Observable.using(create_resource, create_observable)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(200, ex))
        assert(0 == create_invoked[0])
        assert(1 == dispose_invoked[0])

    def test_using_throw_resource_usage(self):
        scheduler = TestScheduler()
        dispose_invoked = [0]
        create_invoked = [0]
        disposable = [None]
        ex = 'ex'

        def create():
            def create_resource():
                dispose_invoked[0] += 1
                disposable[0] = MockDisposable(scheduler)
                return disposable[0]

            def create_observable(d):
                create_invoked[0] += 1
                _raise(ex)

            return Observable.using(create_resource, create_observable)
        results = scheduler.start(create)

        results.messages.assert_equal(on_error(200, ex))
        assert(1 == create_invoked[0])
        assert(1 == dispose_invoked[0])
        return disposable[0].disposes.assert_equal(200, 200)
