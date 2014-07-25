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

def test_skip_until_somedata_next():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_next(225, 99), on_completed(230)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(230, 4), on_next(240, 5), on_completed(250))

def test_skip_until_somedata_error():
    scheduler = TestScheduler()
    ex = 'ex'
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_error(225, ex)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(225, ex))

def test_skip_until_somedata_empty():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    r_msgs = [on_next(150, 1), on_completed(225)]
    l = scheduler.create_hot_observable(l_msgs)
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_skip_until_never_next():
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_next(225, 2), on_completed(250)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_skip_until_never_error():
    ex = 'ex'
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_error(225, ex)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(225, ex))

def test_skip_until_somedata_never():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    l = scheduler.create_hot_observable(l_msgs)
    r = Observable.never()

    def create():
        return l.skip_until(r)

    results = scheduler.start(create)
    results.messages.assert_equal()

def test_skip_until_never_empty():
    scheduler = TestScheduler()
    r_msgs = [on_next(150, 1), on_completed(225)]
    l = Observable.never()
    r = scheduler.create_hot_observable(r_msgs)
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_skip_until_never_never():
    scheduler = TestScheduler()
    l = Observable.never()
    r = Observable.never()
    
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_skip_until_has_completed_causes_disposal():
    scheduler = TestScheduler()
    l_msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250)]
    disposed = [False]
    l = scheduler.create_hot_observable(l_msgs)
    
    def subscribe(observer):
        disposed[0] = True
    
    r = Observable(subscribe)
        
    def create():
        return l.skip_until(r)
    
    results = scheduler.start(create)
    results.messages.assert_equal()
    assert(disposed[0])


def test_zip_never_never():
    scheduler = TestScheduler()
    o1 = Observable.never()
    o2 = Observable.never()
    
    def create():
        return o1.zip(o2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_zip_never_empty():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_completed(210)]
    o1 = Observable.never()
    o2 = scheduler.create_hot_observable(msgs)

    def create():    
        return o1.zip(o2, lambda x, y: x + y)

    results = scheduler.start(create)    
    results.messages.assert_equal()

def test_zip_empty_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_completed(210)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():    
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(210))

def test_zip_empty_non_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():    
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(215))

def test_zip_non_empty_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(215))

def test_zip_never_non_empty():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs)
    e2 = Observable.never()

    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_zip_non_empty_never():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs)
    e2 = Observable.never()

    def create():
        return e1.zip(e2, lambda x, y: x + y)
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_zip_non_empty_non_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(220, 2 + 3), on_completed(240))

def test_zip_empty_error():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_zip_error_empty():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_zip_never_error():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = Observable.never()
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_zip_error_never():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = Observable.never()
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_zip_error_error():
    ex1 = 'ex1'
    ex2 = 'ex2'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(230, ex1)]
    msgs2 = [on_next(150, 1), on_error(220, ex2)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex2))

def test_zip_some_error():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_zip_error_some():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.zip(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_zip_some_data_asymmetric1():
    scheduler = TestScheduler()
    
    def msgs1_factory():
        results = []
        for i in range(5):
            results.append(on_next(205 + i * 5, i))
        return results
    msgs1 = msgs1_factory()
    
    def msgs2_factory():
        results = []
        for i in range(10):
            results.append(on_next(205 + i * 8, i))
        return results
    msgs2 = msgs2_factory()
    
    length = min(len(msgs1), len(msgs2))
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.zip(e2, lambda x, y: x + y)
        
    results = scheduler.start(create).messages
    assert(length == len(results))
    for i in range(length):
        _sum = msgs1[i].value.value + msgs2[i].value.value
        time = max(msgs1[i].time, msgs2[i].time)
        assert(results[i].value.kind == 'N' and results[i].time == time and results[i].value.value == _sum)
 
def test_zip_some_data_asymmetric2():
    scheduler = TestScheduler()
    def msgs1_factory():
        results = []
        for i in range(10):
            results.append(on_next(205 + i * 5, i))
        
        return results
    msgs1 = msgs1_factory()

    def msgs2_factory():
        results = []
        for i in range(5):
            results.append(on_next(205 + i * 8, i))
        return results
    msgs2 = msgs2_factory()

    length = min(len(msgs1), len(msgs2))
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create).messages
    assert(length == len(results))
    for i in range(length):
        _sum = msgs1[i].value.value + msgs2[i].value.value
        time = max(msgs1[i].time, msgs2[i].time)
        assert(results[i].value.kind == 'N' and results[i].time == time and results[i].value.value == _sum)

def test_zip_some_data_symmetric():
    scheduler = TestScheduler()
    def msgs1_factory():
        results = []
        for i in range(10):
            results.append(on_next(205 + i * 5, i))
        return results
    msgs1 = msgs1_factory()
    
    def msgs2_factory():
        results = []
        for i in range(10):
            results.append(on_next(205 + i * 8, i))
        return results
    msgs2 = msgs2_factory()

    length = min(len(msgs1), len(msgs2))
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.zip(e2, lambda x, y: x + y)
    
    results = scheduler.start(create).messages
    assert(length == len(results))
    for i in range(length):
        _sum = msgs1[i].value.value + msgs2[i].value.value
        time = max(msgs1[i].time, msgs2[i].time)
        assert(results[i].value.kind == 'N' and results[i].time == time and results[i].value.value == _sum)

def test_zip_selector_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(240)]
    msgs2 = [on_next(150, 1), on_next(220, 3), on_next(230, 5), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        def selector(x, y):
            if y == 5:
                raise Exception(ex)
            else:
                return x + y
            
        return e1.zip(e2, selector)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(220, 2 + 3), on_error(230, ex))

def test_combine_latest_never_never():
    scheduler = TestScheduler()
    e1 = Observable.never()
    e2 = Observable.never()

    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)

    results = scheduler.start(create)
    results.messages.assert_equal()

def test_combine_latest_never_empty():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_completed(210)]
    e1 = Observable.never()
    e2 = scheduler.create_hot_observable(msgs)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_combine_latest_empty_never():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_completed(210)]
    e1 = Observable.never()
    e2 = scheduler.create_hot_observable(msgs)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_combine_latest_empty_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_completed(210)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)

    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(210))

def test_combine_latest_empty_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(215))

def test_combine_latest_return_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(210)]
    msgs2 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(215))

def test_combine_latest_never_feturn():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    e1 = scheduler.create_hot_observable(msgs)
    e2 = Observable.never()

    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_combine_latest_return_never():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(215, 2), on_completed(210)]
    e1 = scheduler.create_hot_observable(msgs)
    e2 = Observable.never()

    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_combine_latest_return_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)

    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(220, 2 + 3), on_completed(240))

def test_combine_latest_empty_error():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_error_empty():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_return_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_throw_return():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_throw_throw():
    ex1 = 'ex1'
    ex2 = 'ex2'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(220, ex1)]
    msgs2 = [on_next(150, 1), on_error(230, ex2)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex1))

def test_combine_latest_error_throw():
    ex1 = 'ex1'
    ex2 = 'ex2'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(220, ex1)]
    msgs2 = [on_next(150, 1), on_error(230, ex2)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create) 
    results.messages.assert_equal(on_error(220, ex1))

def test_combine_latest_throw_error():
    ex1 = 'ex1'
    ex2 = 'ex2'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_error(220, ex1)]
    msgs2 = [on_next(150, 1), on_error(230, ex2)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex1))

def test_combine_latest_never_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_error(220, ex)]
    e1 = Observable.never()
    e2 = scheduler.create_hot_observable(msgs)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_throw_never():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_error(220, ex)]
    e1 = Observable.never()
    e2 = scheduler.create_hot_observable(msgs)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_some_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)

    results = scheduler.start(create)    
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_throw_some():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(220, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(220, ex))

def test_combine_latest_throw_after_complete_left():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    msgs2 = [on_next(150, 1), on_error(230, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(230, ex))

def test_combine_latest_throw_after_complete_right():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(220)]
    msgs2 = [on_next(150, 1), on_error(230, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(230, ex))

def test_combine_latest_interleaved_with_tail():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(220, 3), on_next(230, 5), on_next(235, 6), on_next(240, 7), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(220, 2 + 3), on_next(225, 3 + 4), on_next(230, 4 + 5), on_next(235, 4 + 6), on_next(240, 4 + 7), on_completed(250))

def test_combine_latest_consecutive():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(235, 6), on_next(240, 7), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(235, 4 + 6), on_next(240, 4 + 7), on_completed(250))

def test_combine_latest_consecutive_end_with_error_left():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_error(230, ex)]
    msgs2 = [on_next(150, 1), on_next(235, 6), on_next(240, 7), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.combine_latest(e2, lambda x, y: x + y)
    
    results = scheduler.start(create)    
    results.messages.assert_equal(on_error(230, ex))

def test_combine_latest_consecutive_end_with_error_right():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(235, 6), on_next(240, 7), on_error(245, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e2.combine_latest(e1, lambda x, y: x + y)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(235, 4 + 6), on_next(240, 4 + 7), on_error(245, ex))

def test_combine_latest_selector_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(215, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(220, 3), on_completed(240)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)

    def create():
        return e1.combine_latest(e2, lambda x, y: _raise(ex))
    
    results = scheduler.start(create)        
    results.messages.assert_equal(on_error(220, ex))

def test_concat_empty_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(250))

def test_concat_empty_never():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = Observable.never()
    
    def create():
        return e1.concat(e2)
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_concat_never_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = Observable.never()
    def create():
        return e2.concat(e1)

    results = scheduler.start(create)
    results.messages.assert_equal()

def test_Concat_NeverNever():
    scheduler = TestScheduler()
    e1 = Observable.never()
    e2 = Observable.never()
    
    def create():
        return e1.concat(e2)
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_Concat_EmptyThrow():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(250, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(250, ex))

def test_concat_throw_empty():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(230, ex)]
    msgs2 = [on_next(150, 1), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(230, ex))

def test_concat_throw_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(230, ex)]
    msgs2 = [on_next(150, 1), on_error(250, 'ex2')]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)

    def create():
        return e1.concat(e2)
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(230, ex))

def test_concat_return_empty():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)

    def create():
        return e1.concat(e2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_completed(250))

def test_concat_empty_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(240, 2), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(240, 2), on_completed(250))

def test_concat_return_never():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = Observable.never()
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2))

def test_concat_never_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_completed(230)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = Observable.never()
    
    def create():
        return e2.concat(e1)
    
    results = scheduler.start(create)
    results.messages.assert_equal()

def test_concat_return_return():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(220, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_next(240, 3), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(220, 2), on_next(240, 3), on_completed(250))

def test_Concat_ThrowReturn():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_error(230, ex)]
    msgs2 = [on_next(150, 1), on_next(240, 2), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)
    
    def create():
        return e1.concat(e2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_error(230, ex))

def test_concat_return_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(220, 2), on_completed(230)]
    msgs2 = [on_next(150, 1), on_error(250, ex)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)

    def create():
        return e1.concat(e2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(220, 2), on_error(250, ex))

def test_concat_some_data_some_data():
    scheduler = TestScheduler()
    msgs1 = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(225)]
    msgs2 = [on_next(150, 1), on_next(230, 4), on_next(240, 5), on_completed(250)]
    e1 = scheduler.create_hot_observable(msgs1)
    e2 = scheduler.create_hot_observable(msgs2)

    def create():
        return e1.concat(e2)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))

# def test_MergeConcat_Basic():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400))
#     results = scheduler.start(create)
#         return xs.merge(2)
#     
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7), on_next(460, 8), on_next(670, 9), on_next(700, 10), on_completed(760))
#     xs.subscriptions.assert_equal(subscribe(200, 760))
# 
# def test_MergeConcat_Basic_Long():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(300))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400))
#     results = scheduler.start(create)
#         return xs.merge(2)
#     
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7), on_next(460, 8), on_next(690, 9), on_next(720, 10), on_completed(780))
#     xs.subscriptions.assert_equal(subscribe(200, 780))
# 
# def test_MergeConcat_Basic_Wide():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(300))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(420, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(450))
#     results = scheduler.start(create)
#         return xs.merge(3)
#     
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(280, 6), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 7), on_next(380, 8), on_next(630, 9), on_next(660, 10), on_completed(720))
#     xs.subscriptions.assert_equal(subscribe(200, 720))
# 
# def test_MergeConcat_Basic_Late():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(300))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(420, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(750))
#     results = scheduler.start(create)
#         return xs.merge(3)
#     
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(280, 6), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 7), on_next(380, 8), on_next(630, 9), on_next(660, 10), on_completed(750))
#     xs.subscriptions.assert_equal(subscribe(200, 750))
# 
# def test_MergeConcat_Disposed():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400))
#     results = scheduler.startWithDispose(function () {
#         return xs.merge(2)
#     }, 450)
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7))
#     xs.subscriptions.assert_equal(subscribe(200, 450))
# 
# def test_MergeConcat_OuterError():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_completed(130))), on_next(320, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_error(400, ex))
#     results = scheduler.start(create)
#         return xs.merge(2)
#     
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_error(400, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 400))
# 
# def test_MergeConcat_InnerError():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, scheduler.create_cold_observable(on_next(50, 1), on_next(100, 2), on_next(120, 3), on_completed(140))), on_next(260, scheduler.create_cold_observable(on_next(20, 4), on_next(70, 5), on_completed(200))), on_next(270, scheduler.create_cold_observable(on_next(10, 6), on_next(90, 7), on_next(110, 8), on_error(140, ex))), on_next(320, scheduler.create_cold_observable(on_next(210, 9), on_next(240, 10), on_completed(300))), on_completed(400))
#     results = scheduler.start(create)
#         return xs.merge(2)
#     
#     results.messages.assert_equal(on_next(260, 1), on_next(280, 4), on_next(310, 2), on_next(330, 3), on_next(330, 5), on_next(360, 6), on_next(440, 7), on_next(460, 8), on_error(490, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 490))
# 
# def test_ZipWithEnumerable_NeverEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1))
#     n2 = []
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
#     n1.subscriptions.assert_equal(subscribe(200, 1000))
# 
# def test_ZipWithEnumerable_EmptyEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_completed(210))
#     n2 = []
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(210))
#     n1.subscriptions.assert_equal(subscribe(200, 210))
# 
# def test_ZipWithEnumerable_EmptyNonEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_completed(210))
#     n2 = [2]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(210))
#     n1.subscriptions.assert_equal(subscribe(200, 210))
# 
# def test_ZipWithEnumerable_NonEmptyEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_completed(220))
#     n2 = []
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_completed(215))
#     n1.subscriptions.assert_equal(subscribe(200, 215))
# 
# def test_ZipWithEnumerable_NeverNonEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1))
#     n2 = [2]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal()
#     n1.subscriptions.assert_equal(subscribe(200, 1000))
# 
# def test_ZipWithEnumerable_NonEmptyNonEmpty():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_completed(230))
#     n2 = [3]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_next(215, 2 + 3), on_completed(230))
#     n1.subscriptions.assert_equal(subscribe(200, 230))
# 
# def test_ZipWithEnumerable_ErrorEmpty():
#     var ex, n1, n2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_error(220, ex))
#     n2 = []
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
#     n1.subscriptions.assert_equal(subscribe(200, 220))
# 

# def test_ZipWithEnumerable_ErrorSome():
#     var ex, n1, n2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_error(220, ex))
#     n2 = [2]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_error(220, ex))
#     n1.subscriptions.assert_equal(subscribe(200, 220))
# 
# def test_ZipWithEnumerable_SomeDataBothSides():
#     var n1, n2, results, scheduler
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5))
#     n2 = [5, 4, 3, 2]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             return x + y
#         
#     
#     results.messages.assert_equal(on_next(210, 7), on_next(220, 7), on_next(230, 7), on_next(240, 7))
#     n1.subscriptions.assert_equal(subscribe(200, 1000))
# 
# def test_ZipWithEnumerable_SelectorThrows():
#     var ex, n1, n2, results, scheduler
#     ex = 'ex'
#     scheduler = TestScheduler()
#     n1 = scheduler.create_hot_observable(on_next(150, 1), on_next(215, 2), on_next(225, 4), on_completed(240))
#     n2 = [3, 5]
#     results = scheduler.start(create)
#         return n1.zip(n2, function (x, y) {
#             if (y == 5) {
#                 throw ex
#             }
#             return x + y
#         
#     
#     results.messages.assert_equal(on_next(215, 2 + 3), on_error(225, ex))
#     n1.subscriptions.assert_equal(subscribe(200, 225))
# 

# test("Rx.Observable.catchException() does not lose subscription to underlying observable", 12, function () {
#     var subscribes = 0,
#             unsubscribes = 0,
#             tracer = Rx.Observable.create(function (observer) { ++subscribes return function () { ++unsubscribes } ,
#             s

#     // Try it without catchException()
#     s = tracer.subscribe()
#     strictEqual(subscribes, 1, "1 subscribes")
#     strictEqual(unsubscribes, 0, "0 unsubscribes")
#     s.dispose()
#     strictEqual(subscribes, 1, "After dispose: 1 subscribes")
#     strictEqual(unsubscribes, 1, "After dispose: 1 unsubscribes")

#     // Now try again with catchException(Observable):
#     subscribes = unsubscribes = 0
#     s = tracer.catchException(Rx.Observable.never()).subscribe()
#     strictEqual(subscribes, 1, "catchException(Observable): 1 subscribes")
#     strictEqual(unsubscribes, 0, "catchException(Observable): 0 unsubscribes")
#     s.dispose()
#     strictEqual(subscribes, 1, "catchException(Observable): After dispose: 1 subscribes")
#     strictEqual(unsubscribes, 1, "catchException(Observable): After dispose: 1 unsubscribes")

#     // And now try again with catchException(function()):
#     subscribes = unsubscribes = 0
#     s = tracer.catchException(function () { return Rx.Observable.never() .subscribe()
#     strictEqual(subscribes, 1, "catchException(function): 1 subscribes")
#     strictEqual(unsubscribes, 0, "catchException(function): 0 unsubscribes")
#     s.dispose()
#     strictEqual(subscribes, 1, "catchException(function): After dispose: 1 subscribes")
#     strictEqual(unsubscribes, 1, "catchException(function): After dispose: 1 unsubscribes") // this one FAILS (unsubscribes is 0)
# 

if __name__ == '__main__':
    test_combine_latest_return_empty()