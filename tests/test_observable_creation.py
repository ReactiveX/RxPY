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

class BooleanDisposable(object):
    def __init__(self):
        self.is_disposed = False
    
    def dispose(self):
        self.is_disposed = True
        return self.is_disposed

def test_subscribe_to_enumerable_finite():
    enumerable_finite = [1, 2, 3, 4, 5]
    scheduler = TestScheduler()
    
    def create():
        return Observable.from_array(enumerable_finite, scheduler)
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(
                        on_next(201, 1),
                        on_next(202, 2),
                        on_next(203, 3),
                        on_next(204, 4),
                        on_next(205, 5),
                        on_completed(206)
                    )


def test_defer_complete():
    xs = [None]
    invoked = [0]
    scheduler = TestScheduler()

    def create():
        def defer():
            invoked[0] += 1
            xs[0] = scheduler.create_cold_observable(
                                on_next(100, scheduler.clock),
                                on_completed(200)
                            )
            return xs[0]
        return Observable.defer(defer)
    results = scheduler.start(create)
        
    
    results.messages.assert_equal(
                        on_next(300, 200),
                        on_completed(400)
                    )
    assert(1 == invoked[0])
    return xs[0].subscriptions.assert_equal(subscribe(200, 400))


def test_defer_error():
    scheduler = TestScheduler()
    invoked = [0]
    xs = [None]
    ex = 'ex'
    
    def create():
        def defer():
            invoked[0] += 1
            xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_error(200, ex))
            return xs[0]
        return Observable.defer(defer)
            
    results = scheduler.start(create)
        
    results.messages.assert_equal(on_next(300, 200), on_error(400, ex)) 
    assert (1 == invoked[0])
    return xs[0].subscriptions.assert_equal(subscribe(200, 400))

def test_defer_dispose():
    scheduler = TestScheduler()
    invoked = [0]
    xs = [None]

    def create():
        def defer():
            invoked[0] += 1
            xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_next(200, invoked[0]), on_next(1100, 1000))
            return xs[0]
        return Observable.defer(defer)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(300, 200), on_next(400, 1))
    assert(1 == invoked[0])
    return xs[0].subscriptions.assert_equal(subscribe(200, 1000))

def test_defer_throw():
    scheduler = TestScheduler()
    invoked = [0]
    ex = 'ex'

    def create():
        def defer():
            invoked[0] += 1
            raise Exception(ex)

        return Observable.defer(defer)
    results = scheduler.start(create)       
    
    results.messages.assert_equal(on_error(200, ex))
    assert(1 == invoked[0])
        
def test_range_zero():
    scheduler = TestScheduler()

    def create():
        return Observable.range(0, 0, scheduler)

    results = scheduler.start(create)    
    results.messages.assert_equal(on_completed(201))

def test_range_one():
    scheduler = TestScheduler()

    def create():
        return Observable.range(0, 1, scheduler)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(201, 0), on_completed(202))

def test_range_five():
    scheduler = TestScheduler()

    def create():
        return Observable.range(10, 5, scheduler)

    results = scheduler.start(create)
    
    results.messages.assert_equal(
                        on_next(201, 10),
                        on_next(202, 11),
                        on_next(203, 12),
                        on_next(204, 13),
                        on_next(205, 14),
                        on_completed(206))

def test_range_dispose():
    scheduler = TestScheduler()

    def create():
        return Observable.range(-10, 5, scheduler)

    results = scheduler.start(create, disposed=204)
    results.messages.assert_equal(on_next(201, -10), on_next(202, -9), on_next(203, -8))

