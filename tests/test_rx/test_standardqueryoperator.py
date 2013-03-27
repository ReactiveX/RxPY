from datetime import datetime

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import SerialDisposable

from tests import assert_equal

on_next = ReactiveTest.on_next

class RxException(Exception):
    pass

def test_select_throws():

    # Helper function for raising exceptions within lambdas
    def _raise(ex):
        raise RxException(ex)

    try:
        Observable.returnvalue(1) \
            .select(lambda x, y: x) \
            .subscribe(lambda x: _raise("ex"))
    except RxException:
        pass

    try:
        Observable.throw_exception('ex') \
            .select(lambda x, y: x) \
            .subscribe(on_error=lambda ex: _raise(ex))
    except RxException:
        pass

    try:
        Observable.empty() \
            .select(lambda x, y: x) \
            .subscribe(lambda x: x, lambda ex: ex, lambda: _raise('ex'))
    except RxException:
        pass

    try:
        def subscribe(observer):
            _raise('ex')
        
        Observable.create(subscribe) \
            .select(lambda x: x) \
            .subscribe()
    except RxException:
        pass

def test_select_disposeinsideselector():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 1), on_next(200, 2), on_next(500, 3), on_next(600, 4))
    invoked = 0
    results = scheduler.create_observer()
    d = SerialDisposable()

    def projection(x, *args, **kw):
        print("test_select_disposeinsideselector.projection", scheduler.clock)
        nonlocal invoked
        invoked += 1
        
        if scheduler.clock > 400:
            d.dispose()
        return x

    d.disposable = xs.select(projection).dump("test").subscribe(results)

    def action(scheduler, state):
        return d.dispose()

    scheduler.schedule_absolute(ReactiveTest.disposed, action)
    scheduler.start()
    assert_equal(results.messages, on_next(100, 1), on_next(200, 2))
    xs.subscriptions.assert_equal(subscribe(0, 500))
    assert invoked == 3
