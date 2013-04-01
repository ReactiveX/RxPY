import math
from datetime import datetime

from rx.observable import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime
from rx.disposables import SerialDisposable

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

def test_is_prime():
    assert is_prime(1) == False
    assert is_prime(2) == True
    assert is_prime(3) == True
    assert is_prime(4) == False
    assert is_prime(5) == True
    assert is_prime(6) == False


def test_where_complete():
    scheduler = TestScheduler()
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600), on_next(610, 12), on_error(620, 'ex'), on_completed(630))
    
    def factory():
        def predicate(x):
            nonlocal invoked
            invoked += 1
            return is_prime(x)
        
        return xs.where(predicate)
        
    results = scheduler.start_with_create(factory)

    results.messages.assert_equal(on_next(230, 3), on_next(340, 5), on_next(390, 7), on_next(580, 11), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))
    assert invoked == 9

def test_where_true():
    scheduler = TestScheduler()
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))
    
    def factory():
        def predicate(x):
            nonlocal invoked
            invoked += 1
            return True
        return xs.where(predicate)
   
    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))
    assert invoked == 9

def test_where_false():
    scheduler = TestScheduler()
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))
    
    def factory():
        def predicate(x):
            nonlocal invoked
            invoked += 1
            return False

        return xs.where(predicate)

    results = scheduler.start_with_create(factory)

    results.messages.assert_equal(on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))
    assert invoked == 9

def test_where_dispose():
    scheduler = TestScheduler()
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))
    
    def factory():
        def predicate(x):
            nonlocal invoked
            invoked += 1
            return is_prime(x)
        return xs.where(predicate)
    
    results = scheduler.start_with_dispose(factory, 400)
    results.messages.assert_equal(on_next(230, 3), on_next(340, 5), on_next(390, 7))
    xs.subscriptions.assert_equal(subscribe(200, 400))
    assert invoked == 5

def test_where_error():
    scheduler = TestScheduler()
    invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_error(600, ex), on_next(610, 12), on_error(620, 'ex'), on_completed(630))
    
    def factory():
        def predicate(x):
            nonlocal invoked
            invoked += 1
            return is_prime(x)
        return xs.where(predicate)

    results = scheduler.start_with_create(factory)
        
    results.messages.assert_equal(on_next(230, 3), on_next(340, 5), on_next(390, 7), on_next(580, 11), on_error(600, ex))
    xs.subscriptions.assert_equal(subscribe(200, 600))
    assert invoked == 9

def test_where_throw():
    scheduler = TestScheduler()
    invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600), on_next(610, 12), on_error(620, 'ex'), on_completed(630))
    
    def factory():
        def predicate(x):
            nonlocal invoked
            invoked += 1
            if x > 5:
                raise Exception(ex)
            
            return is_prime(x)
        return xs.where(predicate)

    results = scheduler.start_with_create(factory)
        
    results.messages.assert_equal(on_next(230, 3), on_next(340, 5), on_error(380, ex))
    xs.subscriptions.assert_equal(subscribe(200, 380))
    assert invoked == 4

def test_where_dispose_in_predicate():
    scheduler = TestScheduler()
    invoked = 0
    ys = None
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600), on_next(610, 12), on_error(620, 'ex'), on_completed(630))
    results = scheduler.create_observer()
    d = SerialDisposable()
    
    def action(scheduler, state):
        nonlocal ys

        def predicate(x):
            nonlocal invoked
            invoked += 1
            if x == 8:
                d.dispose()
            
            return is_prime(x)
        ys = xs.where(predicate)
        return ys

    scheduler.schedule_absolute(created, action)
    
    def action1(scheduler, state):
        d.disposable = ys.subscribe(results)

    scheduler.schedule_absolute(subscribed, action1)

    def action2(scheduler, state):
        d.dispose()

    scheduler.schedule_absolute(disposed, action2)
    
    scheduler.start()
    results.messages.assert_equal(on_next(230, 3), on_next(340, 5), on_next(390, 7))
    xs.subscriptions.assert_equal(subscribe(200, 450))
    assert invoked == 6

def test_where_index_complete():
    scheduler = TestScheduler()
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600), on_next(610, 12), on_error(620, 'ex'), on_completed(630))
    
    def factory():
        def predicate(x, index):
            nonlocal invoked
            invoked += 1
            return is_prime(x + index * 10)
        
        return xs.where(predicate)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(230, 3), on_next(390, 7), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))
    assert invoked == 9
    
def test_where_index_true():
    scheduler = TestScheduler()
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))

    def factory():
        def predicate(x, index):
            nonlocal invoked
            invoked += 1
            return True

        return xs.where(predicate)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))
    assert invoked == 9

def test_where_index_false():
    scheduler = TestScheduler()
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))

    def factory():
        def predicate(x, index):
            nonlocal invoked
            invoked += 1
            return False
        return xs.where(predicate)
    
    results = scheduler.start_with_create(factory)

    results.messages.assert_equal(on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))
    assert invoked == 9

def test_where_index_dispose():
    scheduler = TestScheduler()
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600))
    
    def factory():
        def predicate(x, index):
            nonlocal invoked
            invoked += 1
            return is_prime(x + index * 10)
        
        return xs.where(predicate)

    results = scheduler.start_with_dispose(factory, 400)
    results.messages.assert_equal(on_next(230, 3), on_next(390, 7))
    xs.subscriptions.assert_equal(subscribe(200, 400))
    assert invoked == 5

def test_where_index_error():
    scheduler = TestScheduler()
    invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_error(600, ex), on_next(610, 12), on_error(620, 'ex'), on_completed(630))
    
    def factory():
        def predicate(x, index):
            nonlocal invoked
            invoked += 1
            return is_prime(x + index * 10)
        return xs.where(predicate)

    results = scheduler.start_with_create(factory)
    
    results.messages.assert_equal(on_next(230, 3), on_next(390, 7), on_error(600, ex))
    xs.subscriptions.assert_equal(subscribe(200, 600))
    assert invoked == 9

def test_where_index_throw():
    scheduler = TestScheduler()
    invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600), on_next(610, 12), on_error(620, 'ex'), on_completed(630))

    def factory():
        def predicate(x, index):
            nonlocal invoked
            invoked += 1
            if x > 5:
                raise Exception(ex)

            return is_prime(x + index * 10)
        return xs.where(predicate)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(230, 3), on_error(380, ex))
    xs.subscriptions.assert_equal(subscribe(200, 380))
    assert invoked == 4

def test_where_index_dispose_in_predicate():
    scheduler = TestScheduler()
    ys = None
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600), on_next(610, 12), on_error(620, 'ex'), on_completed(630))
    results = scheduler.create_observer()
    d = SerialDisposable()
    
    def action1(scheduler, state):
        nonlocal ys
        def predicate(x, index):
            nonlocal invoked
            invoked += 1
            if x == 8:
                d.dispose()
            
            return is_prime(x + index * 10)
        ys = xs.where(predicate)

    scheduler.schedule_absolute(created, action1)
    
    def action2(scheduler, state):
         d.disposable = ys.subscribe(results)

    scheduler.schedule_absolute(subscribed, action2)
    
    def action3(scheduler, state):
        d.dispose()

    scheduler.schedule_absolute(disposed, action3)
    
    scheduler.start()
    results.messages.assert_equal(on_next(230, 3), on_next(390, 7))
    xs.subscriptions.assert_equal(subscribe(200, 450))
    assert invoked == 6
