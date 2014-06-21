from rx import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime, MockDisposable
from rx.disposables import Disposable, SerialDisposable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

def test_all_empty():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.all(lambda x: x > 0)
        
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(250, True), on_completed(250))

def test_all_return():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.all(lambda x: x > 0)

    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(250, True), on_completed(250))

def test_all_return_not_natch():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, -2), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.all(lambda x: x > 0)
    
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(210, False), on_completed(210))

def test_all_some_none_match():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, -2), on_next(220, -3), on_next(230, -4), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.all(lambda x: x > 0)
    
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(210, False), on_completed(210))

def test_all_some_match():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, -2), on_next(220, 3), on_next(230, -4), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.all(lambda x: x > 0)

    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(210, False), on_completed(210))

def test_all_some_all_match():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.all(lambda x: x > 0)
    
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(250, True), on_completed(250))

def test_all_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_error(210, ex)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.all(lambda x: x > 0)
    res = scheduler.start(create=create).messages
    res.assert_equal(on_error(210, ex))

def test_all_never():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.all(lambda x: x > 0)

    res = scheduler.start(create=create).messages
    res.assert_equal()

