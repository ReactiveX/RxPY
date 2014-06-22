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

class RxException(Exception):
    pass

# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)

def test_take_until_preempt_somedata_next():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_next(225, 99), on_completed(230)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_completed(225))

def test_take_until_preempt_somedata_error():
    ex = 'ex'
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_error(225, ex)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_error(225, ex))

def test_take_until_nopreempt_somedata_empty():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_completed(225)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)    
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))


def test_take_until_nopreempt_somedata_never():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    l = scheduler.create_hot_observable(l_msgs)
    r = Observable.never()
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)    
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))

def test_take_until_preempt_never_next():
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_next(225, 2), on_completed(250)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)

    def create():
        return l.take_until(r)

    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(225))

def test_take_until_preempt_never_error():
    ex = 'ex'
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_error(225, ex)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(225, ex))

def test_take_until_nopreempt_never_empty():
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_completed(225)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_take_until_nopreempt_never_never():
    scheduler = TestScheduler()
    l = Observable.never()
    r = Observable.never()
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_Take_until_Preempt_BeforeFirstProduced():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(230, 2), on_completed(240)]
    r_msgs = [on_next(150, 1), on_next(210, 2), on_completed(220)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(210))

def test_take_until_preempt_beforefirstproduced_remain_silent_and_proper_disposed():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_error(215, 'ex'), on_completed(240)]
    r_msgs = [on_next(150, 1), on_next(210, 2), on_completed(220)]
    source_not_disposed = False

    def action():
        nonlocal source_not_disposed

        source_not_disposed = True
    l = scheduler.create_hot_observable(l_msgs).do_action(on_next=action)
    
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_completed(210))
    assert(not source_not_disposed)

def test_take_until_nopreempt_afterlastproduced_proper_disposed_signal():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(230, 2), on_completed(240)]
    r_msgs = [on_next(150, 1), on_next(250, 2), on_completed(260)]
    signal_not_disposed = False
    l = scheduler.create_hot_observable(l_msgs)

    def action():
        nonlocal signal_not_disposed
        signal_not_disposed = True
    r = scheduler.create_hot_observable(r_msgs).do_action(on_next=action)
    
    def create():
        return l.take_until(r)
    
    results = scheduler.start(create)        
    results.messages.assert_equal(on_next(230, 2), on_completed(240))
    assert(not signal_not_disposed)
