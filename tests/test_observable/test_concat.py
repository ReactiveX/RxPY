import unittest

import rx
from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest

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


class TestConcat(unittest.TestCase):
    def test_concat_empty_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == [on_completed(250)]

    def test_concat_empty_never(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = rx.never()

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == []

    def test_concat_never_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = rx.never()

        def create():
            return e2.pipe(ops.concat(e1))

        results = scheduler.start(create)
        assert results.messages == []

    def test_concat_never_never(self):
        scheduler = TestScheduler()
        e1 = rx.never()
        e2 = rx.never()

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == []

    def test_concat_empty_on_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(250, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == [on_error(250, ex)]

    def test_concat_throw_empty(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_error(230, ex)]
        msgs2 = [on_next(150, 1), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == [on_error(230, ex)]

    def test_concat_throw_on_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_error(230, ex)]
        msgs2 = [on_next(150, 1), on_error(250, 'ex2')]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == [on_error(230, ex)]

    def test_concat_return_empty(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_completed(250)]

    def test_concat_empty_return(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_completed(230)]
        msgs2 = [on_next(150, 1), on_next(240, 2), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == [on_next(240, 2), on_completed(250)]

    def test_concat_return_never(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = rx.never()

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2)]

    def test_concat_never_return(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = rx.never()

        def create():
            return e2.pipe(ops.concat(e1))

        results = scheduler.start(create)
        assert results.messages == []

    def test_concat_return_return(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(220, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_next(240, 3), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == [on_next(220, 2), on_next(240, 3), on_completed(250)]

    def test_concat_throw_return(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_error(230, ex)]
        msgs2 = [on_next(150, 1), on_next(240, 2), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == [on_error(230, ex)]

    def test_concat_return_on_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(220, 2), on_completed(230)]
        msgs2 = [on_next(150, 1), on_error(250, ex)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == [on_next(220, 2), on_error(250, ex)]

    def test_concat_some_data_some_data(self):
        scheduler = TestScheduler()
        msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(225)]
        msgs2 = [on_next(150, 1), on_next(230, 4), on_next(240, 5), on_completed(250)]
        e1 = scheduler.create_hot_observable(msgs1)
        e2 = scheduler.create_hot_observable(msgs2)

        def create():
            return e1.pipe(ops.concat(e2))

        results = scheduler.start(create)
        assert results.messages == [on_next(210, 2), on_next(
            220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]

    def test_concat_forward_scheduler(self):
        scheduler = TestScheduler()
        subscribe_schedulers = {'e1': 'unknown', 'e2': 'unknown'}

        def subscribe_e1(observer, scheduler='not_set'):
            subscribe_schedulers['e1'] = scheduler
            observer.on_completed()

        def subscribe_e2(observer, scheduler='not_set'):
            subscribe_schedulers['e2'] = scheduler
            observer.on_completed()

        e1 = rx.create(subscribe_e1)
        e2 = rx.create(subscribe_e2)

        stream = e1.pipe(ops.concat(e2))
        stream.subscribe(scheduler=scheduler)
        scheduler.advance_to(1000)
        assert subscribe_schedulers['e1'] is scheduler
        assert subscribe_schedulers['e2'] is scheduler

    def test_concat_forward_none_scheduler(self):
        subscribe_schedulers = {'e1': 'unknown', 'e2': 'unknown'}

        def subscribe_e1(observer, scheduler='not_set'):
            subscribe_schedulers['e1'] = scheduler
            observer.on_completed()

        def subscribe_e2(observer, scheduler='not_set'):
            subscribe_schedulers['e2'] = scheduler
            observer.on_completed()

        e1 = rx.create(subscribe_e1)
        e2 = rx.create(subscribe_e2)

        stream = e1.pipe(ops.concat(e2))
        stream.subscribe()
        assert subscribe_schedulers['e1'] is None
        assert subscribe_schedulers['e2'] is None
