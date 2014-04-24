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

def test_return_basic():
    scheduler = TestScheduler()

    def factory():
        return Observable.return_value(42, scheduler)
    
    results = scheduler.start(factory)
    results.messages.assert_equal(
                        on_next(201, 42),
                        on_completed(201))

def test_return_disposed():
    scheduler = TestScheduler()

    def factory():
        return Observable.return_value(42, scheduler)
    
    results = scheduler.start(factory, disposed=200)
    results.messages.assert_equal()

def test_return_disposed_after_next():
    scheduler = TestScheduler()
    d = SerialDisposable()
    xs = Observable.return_value(42, scheduler)
    results = scheduler.create_observer()

    def action(scheduler, state):
        def on_next(x):
            d.dispose()
            results.on_next(x)
        def on_error(e):
            results.on_error(e)
        def on_completed():
            results.on_completed()

        d.disposable = xs.subscribe(on_next, on_error, on_completed)
        return d.disposable
    
    scheduler.schedule_absolute(100, action)
    scheduler.start()
    results.messages.assert_equal(on_next(101, 42))

def test_return_observer_throws():
    scheduler1 = TestScheduler()
    xs = Observable.return_value(1, scheduler1)
    xs.subscribe(lambda x: _raise('ex'))
    
    try:
        scheduler1.start()
    except RxException:
        pass
    
    scheduler2 = TestScheduler()
    ys = Observable.return_value(1, scheduler2)
    ys.subscribe(lambda x: x, lambda ex: ex, lambda: _raise('ex'))

    try:
        scheduler2.start()
    except RxException:
        pass

def test_never_basic():
    scheduler = TestScheduler()
    xs = Observable.never()
    results = scheduler.create_observer()
    xs.subscribe(results)
    scheduler.start()
    results.messages.assert_equal()

def test_throw_exception_basic():
    scheduler = TestScheduler()
    ex = 'ex'

    def factory():
        return Observable.throw_exception(ex, scheduler)
    
    results = scheduler.start(factory)
    results.messages.assert_equal(on_error(201, ex))

def test_throw_disposed():
    scheduler = TestScheduler()
    def factory():
        return Observable.throw_exception('ex', scheduler)

    results = scheduler.start(factory, disposed=200)
    results.messages.assert_equal()

def test_throw_observer_throws():
    scheduler = TestScheduler()
    xs = Observable.throw_exception('ex', scheduler)
    xs.subscribe(lambda x: None, lambda ex: _raise('ex'), lambda: None)
    
    try:
        return scheduler.start()
    except RxException:
        pass

def test_empty_basic():
    scheduler = TestScheduler()

    def factory():
        return Observable.empty(scheduler)
    results = scheduler.start(factory)
    
    results.messages.assert_equal(on_completed(201))

def test_empty_disposed():
    scheduler = TestScheduler()

    def factory():
        return Observable.empty(scheduler)
    
    results = scheduler.start(factory, disposed=200)
    results.messages.assert_equal()

def test_empty_observer_throw_exception():
    scheduler = TestScheduler()
    xs = Observable.empty(scheduler)
    xs.subscribe(lambda x: None, lambda ex: None, lambda: _raise('ex'))
    
    try:
        return scheduler.start()
    except RxException:
        pass
    
def test__subscribe_to_enumerable_finite():
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

def test_generate_finite():
    scheduler = TestScheduler()

    def create():
        return Observable.generate(0, 
            lambda x: x <= 3,
            lambda x: x + 1,
            lambda x: x,
            scheduler)
    
    results = scheduler.start(create)
        
    results.messages.assert_equal(
                        on_next(201, 0),
                        on_next(202, 1),
                        on_next(203, 2),
                        on_next(204, 3),
                        on_completed(205)
                    )

def test_generate_throw_condition():
    scheduler = TestScheduler()
    ex = 'ex'

    def create():
        return Observable.generate(0, 
            lambda x: _raise('ex'),
            lambda x: x + 1,
            lambda x: x,
            scheduler)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(201, ex))

def test_generate_throw_result_selector():
    scheduler = TestScheduler()
    ex = 'ex'

    def create():
        return Observable.generate(0, 
            lambda x: True,
            lambda x: x + 1,
            lambda x: _raise('ex'),
            scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_generate_throw_iterate():
    scheduler = TestScheduler()
    ex = 'ex'

    def create():
        return Observable.generate(0, 
            lambda x: True,
            lambda x: _raise(ex),
            lambda x: x,
            scheduler)
    results = scheduler.start(create)
    
    results.messages.assert_equal(
                        on_next(201, 0),
                        on_error(202, ex)
                    )

def test_generate_dispose():
    scheduler = TestScheduler()
    ex = 'ex'

    def create():
        return Observable.generate(0, 
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            scheduler)

    results = scheduler.start(create, disposed=203)
    results.messages.assert_equal(
                        on_next(201, 0),
                        on_next(202, 1))

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

def test_using_null():
    disposable = [None]
    xs = [None]
    _d = [None]

    scheduler = TestScheduler()
    dispose_invoked = [0]
    create_invoked = [0]

    def create():
        def create_resources():
            dispose_invoked[0] += 1
            disposable[0] = None
            return disposable[0]

        def create_observable(d):
            _d[0] = d
            create_invoked[0] += 1
            xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_completed(200))
            return xs[0]
        return Observable.using(create_resources, create_observable)
        
    results = scheduler.start(create)
    
    assert(disposable[0] == _d[0])
    results.messages.assert_equal(on_next(300, 200), on_completed(400))
    assert(1 == create_invoked[0])
    assert(1 == dispose_invoked[0])
    xs[0].subscriptions.assert_equal(subscribe(200, 400))
    assert(disposable[0] == None)

def test_using_complete():
    disposable = [None]
    xs = [None]
    _d = [None]
    scheduler = TestScheduler()
    dispose_invoked = [0]
    create_invoked = [0]
    
    def create():
        def create_resource():
            dispose_invoked[0] += 1
            disposable[0] = MockDisposable(scheduler)
            return disposable[0]
        def create_observable(d):
            _d[0] = d
            create_invoked[0] += 1
            xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_completed(200))
            return xs[0]
        return Observable.using(create_resource, create_observable)
        
    results = scheduler.start(create)
    
    assert(disposable == _d)
    results.messages.assert_equal(on_next(300, 200), on_completed(400))
    assert(create_invoked[0] == 1)
    assert(dispose_invoked[0] == 1)
    xs[0].subscriptions.assert_equal(subscribe(200, 400))
    disposable[0].disposes.assert_equal(200, 400)


def test_using_error():
    scheduler = TestScheduler()
    dispose_invoked = [0]
    create_invoked = [0]
    ex = 'ex'
    disposable = [None]
    xs = [None]
    _d = [None]
    
    def create():
        def create_resource():
            dispose_invoked[0] += 1
            disposable[0] = MockDisposable(scheduler)
            return disposable[0]
        def create_observable(d):
            _d[0] = d
            create_invoked[0] += 1
            xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_error(200, ex))
            return xs[0]
        return Observable.using(create_resource, create_observable)
    results = scheduler.start(create)
    
    assert (disposable[0] == _d[0])
    results.messages.assert_equal(on_next(300, 200), on_error(400, ex))
    assert(create_invoked[0] == 1)
    assert(dispose_invoked[0] == 1)
    xs[0].subscriptions.assert_equal(subscribe(200, 400))
    disposable[0].disposes.assert_equal(200, 400)

def test_using_dispose():
    disposable = [None]
    xs = [None]
    _d = [None]
    scheduler = TestScheduler()
    dispose_invoked = [0]
    create_invoked = [0]

    def create():
        def create_resource():
            dispose_invoked[0] += 1
            disposable[0] = MockDisposable(scheduler)
            return disposable[0]
        def create_observable(d):
            _d[0] = d
            create_invoked[0] += 1
            xs[0] = scheduler.create_cold_observable(on_next(100, scheduler.clock), on_next(1000, scheduler.clock + 1))
            return xs[0]
        return Observable.using(create_resource, create_observable)
    results = scheduler.start(create)
    
    assert(disposable[0] == _d[0])
    results.messages.assert_equal(on_next(300, 200))
    assert(1 == create_invoked[0])
    assert(1 == dispose_invoked[0])
    xs[0].subscriptions.assert_equal(subscribe(200, 1000))
    disposable[0].disposes.assert_equal(200, 1000)


def test_using_throw_resource_selector():
    scheduler = TestScheduler()
    dispose_invoked = [0]
    create_invoked = [0]
    ex = 'ex'
    
    def create():
        def create_resource():
            dispose_invoked[0] += 1
            raise _raise(ex)
        def create_observable(d):
            create_invoked[0] += 1
            return Observable.never()
        
        return Observable.using(create_resource, create_observable)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(200, ex))
    assert(0 == create_invoked[0])
    assert(1 == dispose_invoked[0])

def test_using_throw_resource_usage():
    scheduler = TestScheduler()
    dispose_invoked = [0]
    create_invoked = [0]
    disposable = [None]
    ex = 'ex'
    
    def create():
        def create_resource():
            dispose_invoked[0] += 1
            disposable[0] = MockDisposable(scheduler)
            return disposable[0]
        
        def create_observable(d):
            create_invoked[0] += 1
            _raise(ex)

        return Observable.using(create_resource, create_observable)
    results = scheduler.start(create)

    results.messages.assert_equal(on_error(200, ex))
    assert(1 == create_invoked[0])
    assert(1 == dispose_invoked[0])
    return disposable[0].disposes.assert_equal(200, 200)

def test_create_next():
    scheduler = TestScheduler()
    def create():
        def subscribe(o):
            o.on_next(1)
            o.on_next(2)
            return lambda: None
        return Observable.create(subscribe)

    results = scheduler.start(create)        
    results.messages.assert_equal(on_next(200, 1), on_next(200, 2))

def test_create_completed():
    scheduler = TestScheduler()
    
    def create():
        def subscribe(o):
            o.on_completed()
            o.on_next(100)
            o.on_error('ex')
            o.on_completed()
            return lambda: None
        return Observable.create(subscribe)
      
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(200))

def test_create_error():
    scheduler = TestScheduler()
    ex = 'ex'

    def create():
        def subscribe(o):
            o.on_error(ex)
            o.on_next(100)
            o.on_error('foo')
            o.on_completed()
            return lambda: None
        return Observable.create(subscribe)

    results = scheduler.start(create)      
    results.messages.assert_equal(on_error(200, ex))


def test_create_exception():
    try:
        return Observable.create(lambda o: _raise('ex')).subscribe()
    except RxException:
        pass

def test_create_dispose():
    scheduler = TestScheduler()

    def create():    
        def subscribe(o):
            is_stopped = [False]
            o.on_next(1)
            o.on_next(2)

            def action1(scheduler, state):
                if not is_stopped[0]:
                    return o.on_next(3)
            scheduler.schedule_relative(600, action1)
            
            def action2(scheduler, state):
                if not is_stopped[0]:
                    return o.on_next(4)
            scheduler.schedule_relative(700, action2)
            
            def action3(scheduler, state):
                if not is_stopped[0]:
                    return o.on_next(5)
            scheduler.schedule_relative(900, action3)
            
            def action4(scheduler, state):
                if not is_stopped[0]:
                    return o.on_next(6)
            scheduler.schedule_relative(1100, action4)
            
            def dispose():
                is_stopped[0] = True
            return dispose
        return Observable.create(subscribe)
        
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(200, 1), on_next(200, 2), on_next(800, 3), on_next(900, 4))


def test_create_observer_throws():
    def subscribe(o):
        o.on_next(1)
        return lambda: None
    try:
        return Observable.create(subscribe).subscribe(lambda x: _raise('ex'))
    except RxException:
        pass

    def subscribe2(o):
        o.on_error('exception')
        return lambda: None
    try:
        return Observable.create(subscribe2).subscribe(on_error=lambda ex: _raise('ex'))
    except RxException:
        pass
    
    def subscribe3(o):
        o.on_completed()
        return lambda: None
    try:
        return Observable.create(subscribe3).subscribe(on_complete=lambda: _raise('ex'))
    except RxException:
        pass

def test_create_with_disposable_next():
    scheduler = TestScheduler()
    def create():
        def subscribe(o):
            o.on_next(1)
            o.on_next(2)
            return Disposable.empty()
        return Observable.create_with_disposable(subscribe)
    results = scheduler.start(create)

    results.messages.assert_equal(on_next(200, 1), on_next(200, 2))


def test_create_with_disposable_completed():
    scheduler = TestScheduler()
    def create():
        def subscribe(o):
            o.on_completed()
            o.on_next(100)
            o.on_error('ex')
            o.on_completed()
            return Disposable.empty()
        return Observable.create_with_disposable(subscribe)
        
    results = scheduler.start(create)
    results.messages.assert_equal(on_completed(200))

def test_create_with_disposable_error():
    scheduler = TestScheduler()
    ex = 'ex'
    def create():
        def subscribe(o):
            o.on_error(ex)
            o.on_next(100)
            o.on_error('foo')
            o.on_completed()
            return Disposable.empty()

        return Observable.create_with_disposable(subscribe)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_error(200, ex))

def test_create_with_disposable_exception():
    try:
        return Observable.create_with_disposable(lambda: o, _raise('ex')).subscribe()
    except RxException:
        pass

def test_create_with_disposable_dispose():
    scheduler = TestScheduler()

    def create():
        def subscribe(o):
            d = BooleanDisposable()
            o.on_next(1)
            o.on_next(2)

            def action1(scheduler, state):
                if not d.is_disposed:
                    o.on_next(3)
            scheduler.schedule_relative(600, action1)
            
            def action2(scheduler, state):
                if not d.is_disposed:
                    o.on_next(4)
            scheduler.schedule_relative(700, action2)

            def action3(scheduler, state):
                if not d.is_disposed:
                    o.on_next(5)
            scheduler.schedule_relative(900, action3)
            
            def action4(scheduler, state):
                if not d.is_disposed:
                    o.on_next(6)
            scheduler.schedule_relative(1100, action4)
            
            return d
        return Observable.create_with_disposable(subscribe)
        
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_next(200, 1), on_next(200, 2), on_next(800, 3), on_next(900, 4))


def test_create_with_disposable_observer_throws():
    def subscribe1(o):
        o.on_next(1)
        return Disposable.empty()

    def on_next(x):
        _raise('ex')

    try:
        return Observable.create_with_disposable(subscribe1).subscribe(on_next)
    except RxException:
        pass
    
    def subscribe2(o):
        o.on_error('exception')
        return Disposable.empty()

    try:
        return Observable.create_with_disposable(subscribe2).subscribe(on_error=lambda ex: _raise('ex'))
    except RxException:
        pass
    
    def subscribe3(o):
        o.on_completed()
        return Disposable.empty()

    try:
        return Observable.create_with_disposable(subscribe3).subscribe(on_completed=_raise('ex'))
    except RxException:
        pass
        
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

def test_repeat_observable_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(
                        on_next(100, 1),
                        on_next(150, 2),
                        on_next(200, 3),
                        on_completed(250))
    results = scheduler.start(lambda: xs.repeat())
    
    results.messages.assert_equal(
                        on_next(300, 1),
                        on_next(350, 2),
                        on_next(400, 3),
                        on_next(550, 1),
                        on_next(600, 2),
                        on_next(650, 3),
                        on_next(800, 1),
                        on_next(850, 2),
                        on_next(900, 3))
    xs.subscriptions.assert_equal(
                        subscribe(200, 450),
                        subscribe(450, 700),
                        subscribe(700, 950),
                        subscribe(950, 1000))


def test_repeat_observable_infinite():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
    results = scheduler.start(lambda: xs.repeat())
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3))
    return xs.subscriptions.assert_equal(subscribe(200, 1000))

def test_repeat_observable_error():
    results = None
    scheduler = TestScheduler()
    ex = 'ex'
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_error(250, ex))
    results = scheduler.start(lambda: xs.repeat())
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_error(450, ex))
    return xs.subscriptions.assert_equal(subscribe(200, 450))


def test_repeat_observable_throws():
    scheduler1 = TestScheduler()
    xs = Observable.return_value(1, scheduler1).repeat()
    xs.subscribe(lambda x: _raise('ex'))
    
    try:
        return scheduler1.start()
    except RxException:
        pass

    scheduler2 = TestScheduler()
    ys = Observable.throw_exception('ex', scheduler2).repeat()
    ys.subscribe(lambda ex: _raise('ex'))
    
    try:
        return scheduler2.start()
    except RxException:
        pass

    scheduler3 = TestScheduler()
    zs = Observable.return_value(1, scheduler3).repeat()
    d = zs.subscribe(lambda: _raise('ex'))
    
    scheduler3.schedule_absolute(210, lambda: d.dispose())
    
    scheduler3.start()
    xss = Observable.create(lambda o: _raise('ex')).repeat()
    try:
        return xss.subscribe()
    except RxException:
        pass

def test_repeat_observable_repeat_count_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_completed(20))
    results = scheduler.start(lambda: xs.repeat(3))
    
    results.messages.assert_equal(on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(230, 2), on_next(235, 3), on_next(245, 1), on_next(250, 2), on_next(255, 3), on_completed(260))
    xs.subscriptions.assert_equal(subscribe(200, 220), subscribe(220, 240), subscribe(240, 260))

def test_repeat_observable_repeat_count_dispose():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_completed(20))
    results = scheduler.start(lambda: xs.repeat(3), disposed=231)
    results.messages.assert_equal(on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(230, 2))
    return xs.subscriptions.assert_equal(subscribe(200, 220), subscribe(220, 231))

def test_repeat_observable_repeat_count_infinite():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
    results = scheduler.start(lambda: xs.repeat(3))
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3))
    return xs.subscriptions.assert_equal(subscribe(200, 1000))

def test_repeat_observable_repeat_count_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_error(250, ex))
    results = scheduler.start(lambda: xs.repeat(3))
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_error(450, ex))
    return xs.subscriptions.assert_equal(subscribe(200, 450))


def test_repeat_observable_repeat_count_throws():
    scheduler1 = TestScheduler()
    xs = Observable.return_value(1, scheduler1).repeat(3)
    xs.subscribe(lambda x: _raise('ex'))
    
    try:
        return scheduler1.start()
    except RxException:
        pass

    scheduler2 = TestScheduler()
    ys = Observable.throwException('ex1', scheduler2).repeat(3)
    ys.subscribe(lambda ex: _raise('ex2'))
    
    try:
        return scheduler2.start()
    except RxException:
        pass

    scheduler3 = TestScheduler()
    zs = Observable.return_value(1, scheduler3).repeat(100)
    d = zs.subscribe(on_complete=lambda: _raise('ex3'))
    
    scheduler3.schedule_absolute(10, lambda: d.dispose())
    
    scheduler3.start()
    xss = Observable.create(lambda o: _raise('ex4')).repeat(3)
    try:
        return xss.subscribe()
    except RxException:
        pass

def test_retry_observable_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_completed(250))
    results = scheduler.start(lambda: xs.retry())
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_completed(450))
    xs.subscriptions.assert_equal(subscribe(200, 450))

def test_retry_observable_infinite():
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
    results = scheduler.start(lambda: xs.retry())
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3))
    return xs.subscriptions.assert_equal(subscribe(200, 1000))

def test_retry_observable_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_error(250, ex))
    results = scheduler.start(lambda: xs.retry(), disposed=1100)
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_next(550, 1), on_next(600, 2), on_next(650, 3), on_next(800, 1), on_next(850, 2), on_next(900, 3), on_next(1050, 1))
    return xs.subscriptions.assert_equal(subscribe(200, 450), subscribe(450, 700), subscribe(700, 950), subscribe(950, 1100))

def test_Retry_Observable_Throws():
    scheduler1 = TestScheduler()
    xs = Observable.return_value(1, scheduler1).retry()
    xs.subscribe(lambda x: _raise('ex'))
    
    try:
        return scheduler1.start()
    except RxException:
        pass

    scheduler2 = TestScheduler()
    ys = Observable.throw_exception('ex', scheduler2).retry()
    d = ys.subscribe(on_error=lambda ex: _raise('ex'))
    
    scheduler2.schedule_absolute(210, lambda: d.dispose())
    
    scheduler2.start()
    scheduler3 = TestScheduler()
    zs = Observable.return_value(1, scheduler3).retry()
    zs.subscribe(on_completed=lambda: _raise('ex'))
    
    try:
        return scheduler3.start()
    except RxException:
        pass

    xss = Observable.create(lambda o: _raise('ex')).retry()
    try:
        return xss.subscribe()
    except RxException:
        pass

def test_retry_observable_retry_count_basic():
    scheduler = TestScheduler()
    ex = 'ex'
    xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_error(20, ex))
    results = scheduler.start(lambda: xs.retry(3))
    
    results.messages.assert_equal(on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(230, 2), on_next(235, 3), on_next(245, 1), on_next(250, 2), on_next(255, 3), on_error(260, ex))
    xs.subscriptions.assert_equal(subscribe(200, 220), subscribe(220, 240), subscribe(240, 260))


def test_retry_observable_retry_count_dispose():
    scheduler = TestScheduler()
    ex = 'ex'
    xs = scheduler.create_cold_observable(on_next(5, 1), on_next(10, 2), on_next(15, 3), on_error(20, ex))
    results = scheduler.start(lambda: xs.retry(3), disposed=231)
    results.messages.assert_equal(on_next(205, 1), on_next(210, 2), on_next(215, 3), on_next(225, 1), on_next(230, 2))
    xs.subscriptions.assert_equal(subscribe(200, 220), subscribe(220, 231))

def test_retry_observable_retry_count_dispose():
    scheduler = TestScheduler()
    ex = 'ex'
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3))
    results = scheduler.start(lambda: xs.retry(3))
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3))
    xs.subscriptions.assert_equal(subscribe(200, 1000))

def test_retry_observable_retry_count_dispose():
    scheduler = TestScheduler()
    ex = 'ex'
    xs = scheduler.create_cold_observable(on_next(100, 1), on_next(150, 2), on_next(200, 3), on_completed(250))
    results = scheduler.start(lambda: xs.retry(3))
    
    results.messages.assert_equal(on_next(300, 1), on_next(350, 2), on_next(400, 3), on_completed(450))
    xs.subscriptions.assert_equal(subscribe(200, 450))


def test_retry_observable_retry_count_throws():
    scheduler1 = TestScheduler()
    xs = Observable.return_value(1, scheduler1).retry(3)
    xs.subscribe(lambda x: _raise('ex'))
    
    try:
        return scheduler1.start()
    except RxException:
        pass

    scheduler2 = TestScheduler()
    ys = Observable.throwException('ex', scheduler2).retry(100)
    d = ys.subscribe(on_error=lambda ex: _raise('ex'))
    
    scheduler2.schedule_absolute(10, lambda: d.dispose())
    
    scheduler2.start()
    scheduler3 = TestScheduler()
    zs = Observable.return_value(1, scheduler3).retry(100)
    zs.subscribe(on_complete=lambda: _raise('ex'))
    
    try:
        return scheduler3.start()
    except RxException:
        pass

    xss = Observable.create(lambda o: _raise('ex')).retry(100)
    try:
        return xss.subscribe()
    except RxException:
        pass

def test_repeat_value_count_zero():
    scheduler = TestScheduler()

    def create():
        return Observable.repeat(42, 0, scheduler)
    results = scheduler.start(create)
    
    results.messages.assert_equal(on_completed(200))


def test_repeat_value_count_one():
    scheduler = TestScheduler()

    def create():
        return Observable.repeat(42, 1, scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(201, 42), on_completed(201))

def test_repeat_value_count_ten():
    scheduler = TestScheduler()
    
    def create():    
        return Observable.repeat(42, 10, scheduler)
    
    results = scheduler.start(create)
    results.messages.assert_equal(on_next(201, 42), on_next(202, 42), on_next(203, 42), on_next(204, 42), on_next(205, 42), on_next(206, 42), on_next(207, 42), on_next(208, 42), on_next(209, 42), on_next(210, 42), on_completed(210))

def test_repeat_value_count_dispose():
    scheduler = TestScheduler()

    def create():
        return Observable.repeat(42, 10, scheduler)

    results = scheduler.start(create, disposed=207)
    results.messages.assert_equal(on_next(201, 42), on_next(202, 42), on_next(203, 42), on_next(204, 42), on_next(205, 42), on_next(206, 42))

def test_repeat_value():
    scheduler = TestScheduler()
    def create():
        return Observable.repeat(42, -1, scheduler)

    results = scheduler.start(create, disposed=207)
    results.messages.assert_equal(on_next(201, 42), on_next(202, 42), on_next(203, 42), on_next(204, 42), on_next(205, 42), on_next(206, 42))

if __name__ == '__main__':
    test_using_throw_resource_usage()
