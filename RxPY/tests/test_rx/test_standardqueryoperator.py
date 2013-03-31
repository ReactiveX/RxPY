import math
from datetime import datetime

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest
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

def test_group_by_with_key_comparer():
    scheduler = TestScheduler()
    key_invoked = 0
    xs = scheduler.create_hot_observable(
                        on_next(90, "error"),
                        on_next(110, "error"),
                        on_next(130, "error"),
                        on_next(220, "  foo"),
                        on_next(240, " FoO "),
                        on_next(270, "baR  "),
                        on_next(310, "foO "),
                        on_next(350, " Baz   "),
                        on_next(360, "  qux "),
                        on_next(390, "   bar"),
                        on_next(420, " BAR  "),
                        on_next(470, "FOO "),
                        on_next(480, "baz  "),
                        on_next(510, " bAZ "),
                        on_next(530, "    fOo    "),
                        on_completed(570),
                        on_next(580, "error"),
                        on_completed(600),
                        on_error(650, 'ex'))

    def factory():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            return x.lower().strip()
        
        return xs.group_by(key_selector, lambda x: x).select(lambda g: g.key)
        
    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"), on_next(360, "qux"), on_completed(570))
    xs.subscriptions.assert_equal(subscribe(200, 570))
    assert(key_invoked == 12)

def test_groupby_outer_complete():
    scheduler = TestScheduler()
    key_invoked = 0
    ele_invoked = 0
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_completed(570), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    
    def factory():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            return x.lower().strip()

        def element_selector(x):
            nonlocal ele_invoked
            ele_invoked += 1
            return x[::-1] # Yes, this is reverse string in Python

        return xs.group_by(key_selector, element_selector).select(lambda g: g.key)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"), on_next(360, "qux"), on_completed(570))
    xs.subscriptions.assert_equal(subscribe(200, 570))
    assert(key_invoked == 12)
    assert(ele_invoked == 12)

def test_group_by_outer_error():
    scheduler = TestScheduler()
    key_invoked = 0
    ele_invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_error(570, ex), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    
    def factory():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            return x.lower().strip()
        def element_selector(x):
            nonlocal ele_invoked
            ele_invoked += 1
            return x[::-1]
        
        return xs.group_by(key_selector, element_selector).select(lambda g: g.key)

    results = scheduler.start_with_create(factory)

    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"), on_next(360, "qux"), on_error(570, ex))
    xs.subscriptions.assert_equal(subscribe(200, 570))
    assert(key_invoked == 12)
    assert(ele_invoked == 12)


def test_group_by_outer_dispose():
    scheduler = TestScheduler()
    key_invoked = 0
    ele_invoked = 0
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_completed(570), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    
    def dispose():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            return x.lower().strip()
        
        def element_selector(x):
            nonlocal ele_invoked
            ele_invoked += 1
            return x[::-1]

        return xs.group_by(key_selector, element_selector).select(lambda g: g.key)

    results = scheduler.start_with_dispose(dispose, 355)
    
    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"))
    xs.subscriptions.assert_equal(subscribe(200, 355))
    assert(key_invoked == 5)
    assert(ele_invoked == 5)

def test_group_by_outer_key_throw():
    scheduler = TestScheduler()
    key_invoked = 0
    ele_invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_completed(570), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    def factory():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            if key_invoked == 10:
                raise Exception(ex)
            
            return x.lower().strip()

        def element_selector(x):
            nonlocal ele_invoked
            ele_invoked += 1
            return x[::-1]
        
        return xs.group_by(key_selector, element_selector).select(lambda g: g.key)
     
    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"), on_next(360, "qux"), on_error(480, ex))
    xs.subscriptions.assert_equal(subscribe(200, 480))
    assert(key_invoked == 10)
    assert(ele_invoked == 9)

def test_group_by_outer_ele_throw():
    scheduler = TestScheduler()
    key_invoked = 0
    ele_invoked = 0
    ex = 'ex'
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_completed(570), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    
    def factory():
        def key_selector(x):
            nonlocal key_invoked
            key_invoked += 1
            return x.lower().strip()
        
        def element_selector(x):
            nonlocal ele_invoked
            ele_invoked += 1
            if ele_invoked == 10:
                raise Exception(ex)
            return x[::-1]

        return xs.group_by(key_selector, element_selector).select(lambda g: g.key)

    results = scheduler.start_with_create(factory)
    results.messages.assert_equal(on_next(220, "foo"), on_next(270, "bar"), on_next(350, "baz"), on_next(360, "qux"), on_error(480, ex))
    xs.subscriptions.assert_equal(subscribe(200, 480))
    assert(key_invoked == 10)
    assert(ele_invoked == 10)

def test_group_by_inner_complete():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(90, "error"), on_next(110, "error"), on_next(130, "error"), on_next(220, "  foo"), on_next(240, " FoO "), on_next(270, "baR  "), on_next(310, "foO "), on_next(350, " Baz   "), on_next(360, "  qux "), on_next(390, "   bar"), on_next(420, " BAR  "), on_next(470, "FOO "), on_next(480, "baz  "), on_next(510, " bAZ "), on_next(530, "    fOo    "), on_completed(570), on_next(580, "error"), on_completed(600), on_error(650, 'ex'))
    outer_subscription = None
    inner_subscriptions = {}
    inners = {}
    results = {}
    outer = None

    def action1(scheduler, state):
        nonlocal outer
        outer = xs.group_by(lambda x: x.lower().strip(), lambda x: x[::-1])
    
    scheduler.schedule_absolute(created, action1)
    
    def action2(scheduler, state):
        nonlocal outer_subscription

        def next(group):
            nonlocal results, inners

            result = scheduler.create_observer()
            inners[group.key] = group
            results[group.key] = result

            def action21(scheduler, state):
                nonlocal inner_subscriptions
                inner_subscriptions[group.key] = group.subscribe(result)

            scheduler.schedule_relative(100, action21)
        outer_subscription = outer.subscribe(next)
    scheduler.schedule_absolute(subscribed, action2)
    
    def action3(scheduler, state):
        outer_subscription.dispose()
        for sub in inner_subscriptions.values():
            sub.dispose()
        
    scheduler.schedule_absolute(disposed, action3)
    scheduler.start()
    assert(len(inners) == 4)
    results['foo'].messages.assert_equal(on_next(470, " OOF"), on_next(530, "    oOf    "), on_completed(570))
    results['bar'].messages.assert_equal(on_next(390, "rab   "), on_next(420, "  RAB "), on_completed(570))
    results['baz'].messages.assert_equal(on_next(480, "  zab"), on_next(510, " ZAb "), on_completed(570))
    results['qux'].messages.assert_equal(on_completed(570))
    xs.subscriptions.assert_equal(subscribe(200, 570))



if __name__ == '__main__':
    test_group_by_inner_complete()