import math
from datetime import datetime

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import SerialDisposable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
disposed = ReactiveTest.disposed

class RxException(Exception):
    pass

# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)

def test_select_throws():
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
        #print("projection()", scheduler.clock)
        nonlocal invoked
        invoked += 1
        
        if scheduler.clock > 400:
            #print("*** Dispose ****")
            d.dispose()
        return x

    d.disposable = xs.select(projection).subscribe(results)

    def action(scheduler, state):
        """Test:action"""
        #print ("**************action()")
        return d.dispose()

    scheduler.schedule_absolute(ReactiveTest.disposed, action)
    scheduler.start()
    
    results.messages.assert_equal(on_next(100, 1), on_next(200, 2))
    xs.subscriptions.assert_equal(ReactiveTest.subscribe(0, 500))
    
    assert invoked == 3

def test_select_completed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(240, 3), on_next(290, 4), on_next(350, 5), on_completed(400), on_next(410, -1), on_completed(420), on_error(430, 'ex'))
    invoked = 0
    
    def factory():
        def projection(x):
            nonlocal invoked
            invoked += 1
            return x + 1

        return xs.select(projection)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_next(290, 5), on_next(350, 6), on_completed(400))
    xs.subscriptions.assert_equal(ReactiveTest.subscribe(200, 400))
    assert invoked == 4


def test_select_completed_two():
    for i in range(100):
        scheduler = TestScheduler()
        invoked = 0

        xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(240, 3), on_next(290, 4), on_next(350, 5), on_completed(400), on_next(410, -1), on_completed(420), on_error(430, 'ex'))
        def factory():
            def projection(x):
                nonlocal invoked
                invoked +=1
                return x + 1
            return xs.select(projection)

        results = scheduler.start_with_create(factory)
        results.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_next(290, 5), on_next(350, 6), on_completed(400))
        xs.subscriptions.assert_equal(subscribe(200, 400))
        assert invoked == 4

def test_select_not_completed():
    scheduler = TestScheduler()
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(240, 3), on_next(290, 4), on_next(350, 5))
    
    def factory():
        def projection(x):
            nonlocal invoked
            invoked += 1
            return x + 1
        
        return xs.select(projection)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_next(290, 5), on_next(350, 6))
    xs.subscriptions.assert_equal(subscribe(200, 1000))
    assert invoked == 4

def test_select_error():
    scheduler = TestScheduler()
    ex = 'ex'
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(240, 3), on_next(290, 4), on_next(350, 5), on_error(400, ex), on_next(410, -1), on_completed(420), on_error(430, 'ex'))
    def factory():
        def projection(x):
            nonlocal invoked
            invoked += 1 
            return x + 1
        return xs.select(projection)
            
    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_next(290, 5), on_next(350, 6), on_error(400, ex))
    xs.subscriptions.assert_equal(subscribe(200, 400))
    assert invoked == 4

def test_select_selector_throws():
    scheduler = TestScheduler()
    invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(180, 1), on_next(210, 2), on_next(240, 3), on_next(290, 4), on_next(350, 5), on_completed(400), on_next(410, -1), on_completed(420), on_error(430, 'ex'))
    
    def factory():
        def projection (x):
            nonlocal invoked
            invoked += 1
            if invoked == 3:
                raise Exception(ex)
            
            return x + 1
        return xs.select(projection)
      
    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(210, 3), on_next(240, 4), on_error(290, ex))
    xs.subscriptions.assert_equal(subscribe(200, 290))
    assert invoked == 3

def test_select_with_index_throws():
    try:
        return Observable.returnvalue(1) \
            .select(lambda x, index: x) \
            .subscribe(lambda x: _raise('ex'))
    except RxException:
        pass

    try:
        return Observable.throw_exception('ex') \
            .select(lambda x, index: x) \
            .subscribe(lambda x: x, lambda ex: _raise(ex))
    except RxException:
        pass

    try:
        return Observable.empty() \
            .select(lambda x, index: x) \
            .subscribe(lambda x: x, lambda ex: ex, lambda : _raise('ex'))
    except RxException:
        pass

    try:
        return Observable.create(lambda o: _raise('ex')) \
            .select(lambda x, index: x) \
            .subscribe()
    except RxException:
        pass

def test_select_with_index_dispose_inside_selector():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(100, 4), on_next(200, 3), on_next(500, 2), on_next(600, 1))
    invoked = 0
    results = scheduler.create_observer()
    d = SerialDisposable()
    
    def projection(x, index):
        nonlocal invoked
        invoked += 1
        if scheduler.clock > 400:
            d.dispose()
        
        return x + index * 10

    d.disposable = xs.select(projection).subscribe(results)

    def action(scheduler, state):
        return d.dispose()

    scheduler.schedule_absolute(disposed, action)
    scheduler.start()
    results.messages.assert_equal(on_next(100, 4), on_next(200, 13))
    xs.subscriptions.assert_equal(subscribe(0, 500))
    assert invoked == 3

def test_select_with_index_completed():
    scheduler = TestScheduler()
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(180, 5), on_next(210, 4), on_next(240, 3), on_next(290, 2), on_next(350, 1), on_completed(400), on_next(410, -1), on_completed(420), on_error(430, 'ex'))
    
    def factory():
        def projection(x, index):
            nonlocal invoked
            invoked += 1
            return (x + 1) + (index * 10)
        
        return xs.select(projection)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(210, 5), on_next(240, 14), on_next(290, 23), on_next(350, 32), on_completed(400))
    xs.subscriptions.assert_equal(subscribe(200, 400))
    assert invoked == 4

def test_select_with_index_not_completed():
    scheduler = TestScheduler()
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(180, 5), on_next(210, 4), on_next(240, 3), on_next(290, 2), on_next(350, 1))
    def factory():
        def projection(x, index):
            nonlocal invoked
            invoked += 1
            return (x + 1) + (index * 10)

        return xs.select(projection)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(210, 5), on_next(240, 14), on_next(290, 23), on_next(350, 32))
    xs.subscriptions.assert_equal(subscribe(200, 1000))
    assert invoked == 4

def test_select_with_index_error():
    scheduler = TestScheduler()
    ex = 'ex'
    invoked = 0
    xs = scheduler.create_hot_observable(on_next(180, 5), on_next(210, 4), on_next(240, 3), on_next(290, 2), on_next(350, 1), on_error(400, ex), on_next(410, -1), on_completed(420), on_error(430, 'ex'))
    
    def factory():
        def projection(x, index):
            nonlocal invoked
            invoked += 1
            return (x + 1) + (index * 10)
        
        return xs.select(projection)

    results = scheduler.start_with_create(factory)
        
    results.messages.assert_equal(on_next(210, 5), on_next(240, 14), on_next(290, 23), on_next(350, 32), on_error(400, ex))
    xs.subscriptions.assert_equal(subscribe(200, 400))
    assert invoked == 4

def test_select_with_index_selector_throws():
    scheduler = TestScheduler()
    invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(180, 5), on_next(210, 4), on_next(240, 3), on_next(290, 2), on_next(350, 1), on_completed(400), on_next(410, -1), on_completed(420), on_error(430, 'ex'))
    
    def factory():
        def projection(x, index):
            nonlocal invoked
            invoked += 1
            if invoked == 3:
                raise Exception(ex)
            return (x + 1) + (index * 10)

        return xs.select(projection)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(210, 5), on_next(240, 14), on_error(290, ex))
    xs.subscriptions.assert_equal(subscribe(200, 290))
    assert invoked == 3

def is_prime(i):
    if i <= 1:
        return False
    
    max = math.floor(math.sqrt(i))
    for j in range(2, max+1):
        if not (i % j):
            return False

    return True

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
    xs = scheduler.create_hot_observable(on_next(110, 1), on_next(180, 2), on_next(230, 3), on_next(270, 4), on_next(340, 5), on_next(380, 6), on_next(390, 7), on_next(450, 8), on_next(470, 9), on_next(560, 10), on_next(580, 11), on_completed(600));
    
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

if __name__ == '__main__':
    test_select_selector_throws()