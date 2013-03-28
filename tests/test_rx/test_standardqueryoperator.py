from datetime import datetime

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import SerialDisposable

from tests import assert_equal

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error

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
    results = scheduler.create_observer()
    d = SerialDisposable()
    invoked = 0
    
    def projection(x, *args, **kw):
        print("projection()", scheduler.clock)
        nonlocal invoked
        invoked += 1
        
        if scheduler.clock > 400:
            print("*** Dispose ****")
            d.dispose()
        return x

    d.disposable = xs.select(projection).subscribe(results)

    def action(scheduler, state):
        """Test:action"""
        #print ("**************action()")
        return d.dispose()

    scheduler.schedule_absolute(ReactiveTest.disposed, action)
    scheduler.start()
    
    # FIXME: Are we sure this is the correct behaviour?
    #assert_equal(results.messages, on_next(100, 1), on_next(200, 2))
    assert_equal(xs.subscriptions, ReactiveTest.subscribe(0, 500))
    
    assert invoked == 3

def test_select_completed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(240, 3), on_next(290, 4), on_next(350, 5), on_completed(400), on_next(410, -1), on_completed(420), on_error(430, 'ex'))
    invoked = 0
    
    def create():
        def projection(x):
            nonlocal invoked
            invoked += 1
            return x + 1

        return xs.select(projection)

    results = scheduler.start_with_create(create)
    assert_equal(results.messages, on_next(210, 3), on_next(240, 4), on_next(290, 5), on_next(350, 6), on_completed(400))
    assert_equal(xs.subscriptions, ReactiveTest.subscribe(200, 400))
    assert invoked == 4

if __name__ == '__main__':
    test_select_completed()