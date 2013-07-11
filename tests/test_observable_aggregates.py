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

def test_aggregate_with_seed_empty():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.aggregate(seed=42, accumulator=lambda acc, x: acc + x)
    
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(250, 42), on_completed(250))

def test_aggregate_with_seed_return():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, 24), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.aggregate(seed=42, accumulator=lambda acc, x: acc + x)
        
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(250, 42 + 24), on_completed(250))

def test_aggregate_with_seed_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_error(210, ex)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.aggregate(seed=42, accumulator=lambda acc, x: acc + x)
        
    res = scheduler.start(create=create).messages
    res.assert_equal(on_error(210, ex))

def test_aggregate_with_seed_never():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.aggregate(seed=42, accumulator=lambda acc, x: acc + x)
    
    res = scheduler.start(create=create).messages
    res.assert_equal()

def test_aggregate_with_seed_range():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, 0), on_next(220, 1), on_next(230, 2), on_next(240, 3), on_next(250, 4), on_completed(260)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.aggregate(seed=42, accumulator=lambda acc, x: acc + x)
        
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(260, 10 + 42), on_completed(260))

def test_aggregate_without_seed_empty():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.aggregate(accumulator=lambda acc, x: acc + x)
        
    res = scheduler.start(create=create).messages
    assert(len(res) == 1)
    assert(res[0].value.kind == 'E' and res[0].value.exception != None)
    assert(res[0].time == 250)

def test_aggregate_without_seed_return():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, 24), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.aggregate(accumulator=lambda acc, x: acc + x)
        
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(250, 24), on_completed(250))

def test_aggregate_without_seed_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_error(210, ex)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.aggregate(accumulator=lambda acc, x: acc + x)
    
    res = scheduler.start(create=create).messages
    res.assert_equal(on_error(210, ex))

def test_aggregate_without_seed_never():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.aggregate(accumulator=lambda acc, x: acc + x)
    
    res = scheduler.start(create=create).messages
    res.assert_equal()

def test_aggregate_without_seed_range():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, 0), on_next(220, 1), on_next(230, 2), on_next(240, 3), on_next(250, 4), on_completed(260)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.aggregate(accumulator=lambda acc, x: acc + x)
    
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(260, 10), on_completed(260))

def test_reduce_with_seed_empty():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.reduce(lambda acc, x: acc + x, 42)
    
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(250, 42), on_completed(250))

def test_reduce_with_seed_return():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, 24), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.reduce(accumulator=lambda acc, x: acc + x, seed=42)
    
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(250, 42 + 24), on_completed(250))

def test_reduce_with_seed_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_error(210, ex)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.reduce(accumulator=lambda acc, x: acc + x, seed=42)

    res = scheduler.start(create=create).messages
    res.assert_equal(on_error(210, ex))

def test_reduce_with_seed_never():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.reduce(accumulator=lambda acc, x: acc + x, seed=42)

    res = scheduler.start(create=create).messages
    res.assert_equal()

def test_reduce_with_seed_range():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, 0), on_next(220, 1), on_next(230, 2), on_next(240, 3), on_next(250, 4), on_completed(260)]
    xs = scheduler.create_hot_observable(msgs)

    def create():
        return xs.reduce(accumulator=lambda acc, x: acc + x, seed=42)

    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(260, 10 + 42), on_completed(260))

def test_reduce_without_seed_empty():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_completed(250)]
    xs = scheduler.create_hot_observable(msgs)
    
    def create():
        return xs.reduce(accumulator=lambda acc, x: acc + x)

    res = scheduler.start(create=create).messages
    assert(len(res) == 1)
    assert(res[0].value.kind == 'E' and res[0].value.exception != None)
    assert(res[0].time == 250)

def test_reduce_without_seed_return():
    scheduler = TestScheduler()
    msgs = [on_next(150, 1), on_next(210, 24), on_completed(250)]
    
    def create():
        return xs.reduce(accumulator=lambda acc, x: acc + x)

    xs = scheduler.create_hot_observable(msgs)
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(250, 24), on_completed(250))

# def test_ReduceWithoutSeed_Throw():
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_error(210, ex)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.reduce(function (acc, x) {
#             return acc + x
        
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_ReduceWithoutSeed_Never():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.reduce(function (acc, x) {
#             return acc + x
        
#     }).messages
#     res.assert_equal()


# def test_ReduceWithoutSeed_Range():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 0), on_next(220, 1), on_next(230, 2), on_next(240, 3), on_next(250, 4), on_completed(260)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.reduce(function (acc, x) {
#             return acc + x
        
#     }).messages
#     res.assert_equal(on_next(260, 10), on_completed(260))


# def test_Any_Empty():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.any()
#     }).messages
#     res.assert_equal(on_next(250, false), on_completed(250))


# def test_Any_Return():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.any()
#     }).messages
#     res.assert_equal(on_next(210, true), on_completed(210))


# def test_Any_Throw():
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_error(210, ex)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.any()
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_Any_Never():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.any()
#     }).messages
#     res.assert_equal()


# def test_Any_Predicate_Empty():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.any(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_next(250, false), on_completed(250))


# def test_Any_Predicate_Return():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.any(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_next(210, true), on_completed(210))


# def test_Any_Predicate_ReturnNotMatch():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, -2), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.any(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_next(250, false), on_completed(250))


# def test_Any_Predicate_SomeNoneMatch():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, -2), on_next(220, -3), on_next(230, -4), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.any(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_next(250, false), on_completed(250))


# def test_Any_Predicate_SomeMatch():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, -2), on_next(220, 3), on_next(230, -4), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.any(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_next(220, true), on_completed(220))


# def test_Any_Predicate_Throw():
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_error(210, ex)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.any(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_Any_Predicate_Never():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.any(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal()


# def test_All_Empty():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.all(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_next(250, true), on_completed(250))


# def test_All_Return():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.all(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_next(250, true), on_completed(250))


# def test_All_ReturnNotMatch():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, -2), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.all(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_next(210, false), on_completed(210))


# def test_All_SomeNoneMatch():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, -2), on_next(220, -3), on_next(230, -4), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.all(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_next(210, false), on_completed(210))


# def test_All_SomeMatch():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, -2), on_next(220, 3), on_next(230, -4), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.all(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_next(210, false), on_completed(210))


# def test_All_SomeAllMatch():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.all(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_next(250, true), on_completed(250))


# def test_All_Throw():
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_error(210, ex)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.all(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_All_Never():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.all(function (x) {
#             return x > 0
        
#     }).messages
#     res.assert_equal()


# def test_Contains_Empty():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.contains(42)
#     }).messages
#     res.assert_equal(on_next(250, false), on_completed(250))

# def test_Contains_ReturnPositive():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.contains(2)
#     }).messages
#     res.assert_equal(on_next(210, true), on_completed(210))


# def test_Contains_ReturnNegative():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.contains(-2)
#     }).messages
#     res.assert_equal(on_next(250, false), on_completed(250))


# def test_Contains_SomePositive():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.contains(3)
#     }).messages
#     res.assert_equal(on_next(220, true), on_completed(220))

# def test_Contains_SomeNegative():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.contains(-3)
#     }).messages
#     res.assert_equal(on_next(250, false), on_completed(250))


# def test_Contains_Throw():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.contains(42)
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_Contains_Never():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.contains(42)
#     }).messages
#     res.assert_equal()


# def test_Contains_ComparerThrows():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2))
#     res = scheduler.start(create=create)
#         return xs.contains(42, function (a, b) {
#             throw ex
        
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_Contains_ComparerContainsValue():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 3), on_next(220, 4), on_next(230, 8), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.contains(42, function (a, b) {
#             return a % 2 == b % 2
        
#     }).messages
#     res.assert_equal(on_next(220, true), on_completed(220))


# def test_Contains_ComparerDoesNotContainValue():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 4), on_next(230, 8), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.contains(21, function (a, b) {
#             return a % 2 == b % 2
        
#     }).messages
#     res.assert_equal(on_next(250, false), on_completed(250))


def test_count_empty():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
    res = scheduler.start(create=lambda: xs.count()).messages
    res.assert_equal(on_next(250, 0), on_completed(250))

def test_count_empty_ii():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))

    def create():
        return xs.count()
            
    res = scheduler.start(create=create).messages
    res.assert_equal(on_next(250, 1), on_completed(250))

def test_count_some():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))
    res = scheduler.start(create=lambda: xs.count()).messages
    res.assert_equal(on_next(250, 3), on_completed(250))

def test_count_throw():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
    res = scheduler.start(create=lambda: xs.count()).messages
    res.assert_equal(on_error(210, ex))

def test_count_never():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1))
    res = scheduler.start(create=lambda: xs.count()).messages
    res.assert_equal()

def test_count_predicate_empty_true():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
    
    def create():
        return xs.count(lambda _: True)
    
    res = scheduler.start(create=create)
    
    res.messages.assert_equal(on_next(250, 0), on_completed(250))
    xs.subscriptions.assert_equal(subscribe(200, 250))

def test_count_predicate_empty_false():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
    
    def create():
        return xs.count(lambda _: False)
    
    res = scheduler.start(create=create)
        
    res.messages.assert_equal(on_next(250, 0), on_completed(250))
    xs.subscriptions.assert_equal(subscribe(200, 250))

def test_count_predicate_return_true():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
    
    def create():
        return xs.count(lambda _: True)
    
    res = scheduler.start(create=create)
        
    res.messages.assert_equal(on_next(250, 1), on_completed(250))
    xs.subscriptions.assert_equal(subscribe(200, 250))

def test_count_predicate_return_false():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
    
    def create():
        return xs.count(lambda _: False)
    
    res = scheduler.start(create=create)
        
    res.messages.assert_equal(on_next(250, 0), on_completed(250))
    xs.subscriptions.assert_equal(subscribe(200, 250))

def test_count_predicate_some_all():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))
    
    def create():
        return xs.count(lambda x: x < 10)
        
    res = scheduler.start(create=create)
        
    res.messages.assert_equal(on_next(250, 3), on_completed(250))
    xs.subscriptions.assert_equal(subscribe(200, 250))

def test_count_predicate_some_none():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))

    def create():
        return xs.count(lambda x: x > 10)

    res = scheduler.start(create=create)
        
    res.messages.assert_equal(on_next(250, 0), on_completed(250))
    xs.subscriptions.assert_equal(subscribe(200, 250))

def test_count_predicate_some_even():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))
    
    def create():
        return xs.count(lambda x: x % 2 == 0)

    res = scheduler.start(create=create)
            
    res.messages.assert_equal(on_next(250, 2), on_completed(250))
    xs.subscriptions.assert_equal(subscribe(200, 250))

def test_count_predicate_throw_true():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))

    def create():
        return xs.count(lambda _: True)

    res = scheduler.start(create=create)
        
    res.messages.assert_equal(on_error(210, ex))
    xs.subscriptions.assert_equal(subscribe(200, 210))

def test_count_predicate_throw_false():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))

    def create():
        return xs.count(lambda _: False)

    res = scheduler.start(create=create)
        
    res.messages.assert_equal(on_error(210, ex))
    xs.subscriptions.assert_equal(subscribe(200, 210))

def test_count_predicate_never():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1))
 
    def create():
        return xs.count(lambda _: True)
 
    res = scheduler.start(create=create)
        
    res.messages.assert_equal()
    xs.subscriptions.assert_equal(subscribe(200, 1000))

def test_count_predicate_predicate_throws():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(230, 3), on_completed(240))

    def create():
        def predicate(x):
            if x == 3:
                raise Exception(ex)
            else:
                return True
            
        return xs.count(predicate)

    res = scheduler.start(create=create)
            
    res.messages.assert_equal(on_error(230, ex))
    xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_Sum_Int32_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.sum()
#     }).messages
#     res.assert_equal(on_next(250, 0), on_completed(250))

# def test_Sum_Int32_Return():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.sum()
#     }).messages
#     res.assert_equal(on_next(250, 2), on_completed(250))


# def test_Sum_Int32_Some():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.sum()
#     }).messages
#     res.assert_equal(on_next(250, 2 + 3 + 4), on_completed(250))


# def test_Sum_Int32_Throw():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.sum()
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_Sum_Int32_Never():
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1))
#     res = scheduler.start(create=create)
#         return xs.sum()
#     }).messages
#     res.assert_equal()


# def test_Sum_Selector_Regular_Int32():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, "fo"), on_next(220, "b"), on_next(230, "qux"), on_completed(240))
#     res = scheduler.start(create=create)
#         return xs.sum(function (x) {
#             return x.length
        
    
#     res.messages.assert_equal(on_next(240, 6), on_completed(240))
#     xs.subscriptions.assert_equal(subscribe(200, 240))


# def test_Min_Int32_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.min()
#     }).messages
#     equal(1, res.length)
#     ok(res[0].value.kind == 'E' and res[0].value.exception != null)
#     ok(res[0].time == 250)


# def test_Min_Int32_Return():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.min()
#     }).messages
#     res.assert_equal(on_next(250, 2), on_completed(250))


# def test_Min_Int32_Some():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.min()
#     }).messages
#     res.assert_equal(on_next(250, 2), on_completed(250))


# def test_Min_Int32_Throw():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.min()
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_Min_Int32_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1))
#     res = scheduler.start(create=create)
#         return xs.min()
#     }).messages
#     res.assert_equal()


# def test_MinOfT_Comparer_Empty():
#     var comparer, res, scheduler, xs
#     scheduler = TestScheduler()
#     comparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a == b) {
#             return 0
#         }
#         return 1
#     }
#     xs = scheduler.create_hot_observable(on_next(150, 'a'), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.min(comparer)
#     }).messages
#     equal(1, res.length)
#     ok(res[0].value.kind == 'E' and res[0].value.exception != null)
#     ok(res[0].time == 250)


# def test_MinOfT_Comparer_Empty():
#     var comparer, res, scheduler, xs
#     scheduler = TestScheduler()
#     comparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a == b) {
#             return 0
#         }
#         return 1
#     }
#     xs = scheduler.create_hot_observable(on_next(150, 'z'), on_next(210, "b"), on_next(220, "c"), on_next(230, "a"), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.min(comparer)
#     }).messages
#     res.assert_equal(on_next(250, "c"), on_completed(250))


# def test_MinOfT_Comparer_Throw():
#     var comparer, ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     comparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a == b) {
#             return 0
#         }
#         return 1
#     }
#     xs = scheduler.create_hot_observable(on_next(150, 'z'), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.min(comparer)
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_MinOfT_Comparer_Never():
#     var comparer, res, scheduler, xs
#     scheduler = TestScheduler()
#     comparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a == b) {
#             return 0
#         }
#         return 1
#     }
#     xs = scheduler.create_hot_observable(on_next(150, 'z'))
#     res = scheduler.start(create=create)
#         return xs.min(comparer)
#     }).messages
#     res.assert_equal()


# def test_MinOfT_ComparerThrows():
#     var comparer, ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     comparer = function (a, b) {
#         throw ex
#     }
#     xs = scheduler.create_hot_observable(on_next(150, 'z'), on_next(210, "b"), on_next(220, "c"), on_next(230, "a"), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.min(comparer)
#     }).messages
#     res.assert_equal(on_error(220, ex))


# def test_MinBy_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, { key: 1, value: 'z' }), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
        
#     }).messages
#     equal(2, res.length)
#     equal(0, res[0].value.value.length)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MinBy_Return():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable
#         (on_next(150, { key: 1, value: 'z' }),
#         on_next(210, { key: 2, value: 'a' }),
#         on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
        
#     }).messages
#     equal(2, res.length)
#     ok(res[0].value.kind == 'N')
#     equal(1, res[0].value.value.length)
#     equal(2, res[0].value.value[0].key)
#     equal('a', res[0].value.value[0].value)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MinBy_Some():
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 3,
#             value: 'b'
#         }), on_next(220, {
#             key: 2,
#             value: 'c'
#         }), on_next(230, {
#             key: 4,
#             value: 'a'
#         }), on_completed(250)
#     ]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
        
#     }).messages
#     equal(2, res.length)
#     ok(res[0].value.kind == 'N')
#     equal(1, res[0].value.value.length)
#     equal(2, res[0].value.value[0].key)
#     equal('c', res[0].value.value[0].value)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MinBy_Multiple():
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 3,
#             value: 'b'
#         }), on_next(215, {
#             key: 2,
#             value: 'd'
#         }), on_next(220, {
#             key: 3,
#             value: 'c'
#         }), on_next(225, {
#             key: 2,
#             value: 'y'
#         }), on_next(230, {
#             key: 4,
#             value: 'a'
#         }), on_next(235, {
#             key: 4,
#             value: 'r'
#         }), on_completed(250)
#     ]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
        
#     }).messages
#     equal(2, res.length)
#     ok(res[0].value.kind == 'N')
#     equal(2, res[0].value.value.length)
#     equal(2, res[0].value.value[0].key)
#     equal('d', res[0].value.value[0].value)
#     equal(2, res[0].value.value[1].key)
#     equal('y', res[0].value.value[1].value)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MinBy_Throw():
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_error(210, ex)
#     ]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
        
#     }).messages
#     res.assert_equal(on_error(210, ex))

# def test_MinBy_Never():
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         })
#     ]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
        
#     }).messages
#     res.assert_equal()


# def test_MinBy_Comparer_Empty():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_completed(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a == b) {
#             return 0
#         }
#         return 1
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     equal(2, res.length)
#     equal(0, res[0].value.value.length)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MinBy_Comparer_Return():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 2,
#             value: 'a'
#         }), on_completed(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a == b) {
#             return 0
#         }
#         return 1
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     equal(2, res.length)
#     ok(res[0].value.kind == 'N')
#     equal(1, res[0].value.value.length)
#     equal(2, res[0].value.value[0].key)
#     equal('a', res[0].value.value[0].value)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MinBy_Comparer_Some():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 3,
#             value: 'b'
#         }), on_next(220, {
#             key: 20,
#             value: 'c'
#         }), on_next(230, {
#             key: 4,
#             value: 'a'
#         }), on_completed(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a == b) {
#             return 0
#         }
#         return 1
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     equal(2, res.length)
#     ok(res[0].value.kind == 'N')
#     equal(1, res[0].value.value.length)
#     equal(20, res[0].value.value[0].key)
#     equal('c', res[0].value.value[0].value)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MinBy_Comparer_Throw():
#     var ex, msgs, res, reverseComparer, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_error(210, ex)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a == b) {
#             return 0
#         }
#         return 1
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_MinBy_Comparer_Never():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         })
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a == b) {
#             return 0
#         }
#         return 1
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     res.assert_equal()


# def test_MinBy_SelectorThrows():
#     var ex, msgs, res, reverseComparer, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 3,
#             value: 'b'
#         }), on_next(220, {
#             key: 2,
#             value: 'c'
#         }), on_next(230, {
#             key: 4,
#             value: 'a'
#         }), on_completed(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a == b) {
#             return 0
#         }
#         return 1
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             throw ex
#         }, reverseComparer)
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_MinBy_ComparerThrows():
#     var ex, msgs, res, reverseComparer, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 3,
#             value: 'b'
#         }), on_next(220, {
#             key: 2,
#             value: 'c'
#         }), on_next(230, {
#             key: 4,
#             value: 'a'
#         }), on_completed(250)
#     ]
#     reverseComparer = function (a, b) {
#         throw ex
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.minBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     res.assert_equal(on_error(220, ex))


# def test_Max_Int32_Empty():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max()
#     }).messages
#     equal(1, res.length)
#     ok(res[0].value.kind == 'E' and res[0].value.exception != null)
#     ok(res[0].time == 250)


# def test_Max_Int32_Return():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max()
#     }).messages
#     res.assert_equal(on_next(250, 2), on_completed(250))


# def test_Max_Int32_Some():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 3), on_next(220, 4), on_next(230, 2), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max()
#     }).messages
#     res.assert_equal(on_next(250, 4), on_completed(250))


# def test_Max_Int32_Throw():
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_error(210, ex)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max()
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_Max_Int32_Never():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max()
#     }).messages
#     res.assert_equal()


# def test_MaxOfT_Comparer_Empty():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_completed(250)]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max(reverseComparer)
#     }).messages
#     equal(1, res.length)
#     ok(res[0].value.kind == 'E' and res[0].value.exception != null)
#     ok(res[0].time == 250)


# def test_MaxOfT_Comparer_Return():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 'z'), on_next(210, 'a'), on_completed(250)]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max(reverseComparer)
#     }).messages
#     res.assert_equal(on_next(250, 'a'), on_completed(250))


# def test_MaxOfT_Comparer_Some():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 'z'), on_next(210, 'b'), on_next(220, 'c'), on_next(230, 'a'), on_completed(250)]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max(reverseComparer)
#     }).messages
#     res.assert_equal(on_next(250, 'a'), on_completed(250))


# def test_MaxOfT_Comparer_Throw():
#     var ex, msgs, res, reverseComparer, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 'z'), on_error(210, ex)]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max(reverseComparer)
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_MaxOfT_Comparer_Never():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 'z')]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max(reverseComparer)
#     }).messages
#     res.assert_equal()


# def test_MaxOfT_ComparerThrows():
#     var ex, msgs, res, reverseComparer, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 'z'), on_next(210, 'b'), on_next(220, 'c'), on_next(230, 'a'), on_completed(250)]
#     reverseComparer = function (a, b) {
#         throw ex
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.max(reverseComparer)
#     }).messages
#     res.assert_equal(on_error(220, ex))


# def test_MaxBy_Empty():
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, { key: 1, value: 'z' }),
#         on_completed(250)
#     ]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
        
#     }).messages
#     equal(2, res.length)
#     equal(0, res[0].value.value.length)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MaxBy_Return():
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 2,
#             value: 'a'
#         }), on_completed(250)
#     ]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
        
#     }).messages
#     equal(2, res.length)
#     ok(res[0].value.kind == 'N')
#     equal(1, res[0].value.value.length)
#     equal(2, res[0].value.value[0].key)
#     equal('a', res[0].value.value[0].value)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MaxBy_Some():
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 3,
#             value: 'b'
#         }), on_next(220, {
#             key: 4,
#             value: 'c'
#         }), on_next(230, {
#             key: 2,
#             value: 'a'
#         }), on_completed(250)
#     ]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
        
#     }).messages
#     equal(2, res.length)
#     ok(res[0].value.kind == 'N')
#     equal(1, res[0].value.value.length)
#     equal(4, res[0].value.value[0].key)
#     equal('c', res[0].value.value[0].value)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MaxBy_Multiple():
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }),
#         on_next(210, {
#             key: 3,
#             value: 'b'
#         }),
#         on_next(215, {
#             key: 2,
#             value: 'd'
#         }),
#         on_next(220, {
#             key: 3,
#             value: 'c'
#         }),
#         on_next(225, {
#             key: 2,
#             value: 'y'
#         }),
#         on_next(230, {
#             key: 4,
#             value: 'a'
#         }),
#         on_next(235, {
#             key: 4,
#             value: 'r'
#         }),
#         on_completed(250)
#     ]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
        
#     }).messages
#     equal(2, res.length)
#     ok(res[0].value.kind == 'N')
#     equal(2, res[0].value.value.length)
#     equal(4, res[0].value.value[0].key)
#     equal('a', res[0].value.value[0].value)
#     equal(4, res[0].value.value[1].key)
#     equal('r', res[0].value.value[1].value)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MaxBy_Throw():
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }),
#         on_error(210, ex)
#     ]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
        
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_MaxBy_Never():
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         })
#     ]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
        
#     }).messages
#     res.assert_equal()


# def test_MaxBy_Comparer_Empty():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }),
#         on_completed(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     equal(2, res.length)
#     equal(0, res[0].value.value.length)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MaxBy_Comparer_Return():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 2,
#             value: 'a'
#         }), on_completed(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     equal(2, res.length)
#     ok(res[0].value.kind == 'N')
#     equal(1, res[0].value.value.length)
#     equal(2, res[0].value.value[0].key)
#     equal('a', res[0].value.value[0].value)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MaxBy_Comparer_Some():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 3,
#             value: 'b'
#         }), on_next(220, {
#             key: 4,
#             value: 'c'
#         }), on_next(230, {
#             key: 2,
#             value: 'a'
#         }), on_completed(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     equal(2, res.length)
#     ok(res[0].value.kind == 'N')
#     equal(1, res[0].value.value.length)
#     equal(2, res[0].value.value[0].key)
#     equal('a', res[0].value.value[0].value)
#     ok(res[1].value.kind == 'C' and res[1].time == 250)


# def test_MaxBy_Comparer_Throw():
#     var ex, msgs, res, reverseComparer, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_error(210, ex)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_MaxBy_Comparer_Never():
#     var msgs, res, reverseComparer, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         })
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     res.assert_equal()


# def test_MaxBy_SelectorThrows():
#     var ex, msgs, res, reverseComparer, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 3,
#             value: 'b'
#         }), on_next(220, {
#             key: 2,
#             value: 'c'
#         }), on_next(230, {
#             key: 4,
#             value: 'a'
#         }), on_completed(250)
#     ]
#     reverseComparer = function (a, b) {
#         if (a > b) {
#             return -1
#         }
#         if (a < b) {
#             return 1
#         }
#         return 0
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             throw ex
#         }, reverseComparer)
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_MaxBy_ComparerThrows():
#     var ex, msgs, res, reverseComparer, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [
#         on_next(150, {
#             key: 1,
#             value: 'z'
#         }), on_next(210, {
#             key: 3,
#             value: 'b'
#         }), on_next(220, {
#             key: 2,
#             value: 'c'
#         }), on_next(230, {
#             key: 4,
#             value: 'a'
#         }), on_completed(250)
#     ]
#     reverseComparer = function (a, b) {
#         throw ex
#     }
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.maxBy(function (x) {
#             return x.key
#         }, reverseComparer)
#     }).messages
#     res.assert_equal(on_error(220, ex))

# def test_average_int32_return():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 2), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.average()
#     }).messages
#     res.assert_equal(on_next(250, 2), on_completed(250))


# def test_Average_Int32_Some():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_next(210, 3), on_next(220, 4), on_next(230, 2), on_completed(250)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.average()
#     }).messages
#     res.assert_equal(on_next(250, 3), on_completed(250))


# def test_Average_Int32_Throw():
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1), on_error(210, ex)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.average()
#     }).messages
#     res.assert_equal(on_error(210, ex))


# def test_Average_Int32_Never():
#     scheduler = TestScheduler()
#     msgs = [on_next(150, 1)]
#     xs = scheduler.create_hot_observable(msgs)
#     res = scheduler.start(create=create)
#         return xs.average()
#     }).messages
#     res.assert_equal()

# def test_Average_Selector_Regular_Int32():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, "b"), on_next(220, "fo"), on_next(230, "qux"), on_completed(240))
#     res = scheduler.start(create=create)
#         return xs.average(function (x) {
#             return x.length
        
    
#     res.messages.assert_equal(on_next(240, 2), on_completed(240))
#     xs.subscriptions.assert_equal(subscribe(200, 240))


# def test_ToArray_Completed():
#     var msgs, results, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [on_next(110, 1), on_next(220, 2), on_next(330, 3), on_next(440, 4), on_next(550, 5), on_completed(660)]
#     xs = scheduler.create_hot_observable(msgs)
#     results = scheduler.start(create=create)
#         return xs.toArray()
#     }).messages
#     equal(2, results.length)
#     equal(660, results[0].time)
#     equal('N', results[0].value.kind)
#     results[0].value.value.assert_equal(2, 3, 4, 5)
#     ok(on_completed(660).equals(results[1]))
#     xs.subscriptions.assert_equal(subscribe(200, 660))


# def test_ToArray_Error():
#     var ex, msgs, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs = [on_next(110, 1), on_next(220, 2), on_next(330, 3), on_next(440, 4), on_next(550, 5), on_error(660, ex)]
#     xs = scheduler.create_hot_observable(msgs)
#     results = scheduler.start(create=create)
#         return xs.toArray()
#     }).messages
#     results.assert_equal(on_error(660, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 660))


# def test_ToArray_Disposed():
#     var msgs, results, scheduler, xs
#     scheduler = TestScheduler()
#     msgs = [on_next(110, 1), on_next(220, 2), on_next(330, 3), on_next(440, 4), on_next(550, 5)]
#     xs = scheduler.create_hot_observable(msgs)
#     results = scheduler.start(create=create)
#         return xs.toArray()
#     }).messages
#     results.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))


# def test_SequenceEqual_Equal():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_completed(720)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return xs.sequenceEqual(ys)
    
#     results.messages.assert_equal(on_next(720, true), on_completed(720))
#     xs.subscriptions.assert_equal(subscribe(200, 720))
#     ys.subscriptions.assert_equal(subscribe(200, 720))


# def test_SequenceEqual_Equal_Sym():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_completed(720)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return ys.sequenceEqual(xs)
    
#     results.messages.assert_equal(on_next(720, true), on_completed(720))
#     xs.subscriptions.assert_equal(subscribe(200, 720))
#     ys.subscriptions.assert_equal(subscribe(200, 720))


# def test_SequenceEqual_NotEqual_Left():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 0), on_next(340, 6), on_next(450, 7), on_completed(510)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_completed(720)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return xs.sequenceEqual(ys)
    
#     results.messages.assert_equal(on_next(310, false), on_completed(310))
#     xs.subscriptions.assert_equal(subscribe(200, 310))
#     ys.subscriptions.assert_equal(subscribe(200, 310))


# def test_SequenceEqual_NotEqual_Left_Sym():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 0), on_next(340, 6), on_next(450, 7), on_completed(510)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_completed(720)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return ys.sequenceEqual(xs)
    
#     results.messages.assert_equal(on_next(310, false), on_completed(310))
#     xs.subscriptions.assert_equal(subscribe(200, 310))
#     ys.subscriptions.assert_equal(subscribe(200, 310))


# def test_SequenceEqual_NotEqual_Right():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_next(350, 8)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return xs.sequenceEqual(ys)
    
#     results.messages.assert_equal(on_next(510, false), on_completed(510))
#     xs.subscriptions.assert_equal(subscribe(200, 510))
#     ys.subscriptions.assert_equal(subscribe(200, 510))


# def test_SequenceEqual_NotEqual_Right_Sym():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_next(350, 8)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return ys.sequenceEqual(xs)
    
#     results.messages.assert_equal(on_next(510, false), on_completed(510))
#     xs.subscriptions.assert_equal(subscribe(200, 510))
#     ys.subscriptions.assert_equal(subscribe(200, 510))


# def test_SequenceEqual_NotEqual_2():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_next(490, 8), on_next(520, 9), on_next(580, 10), on_next(600, 11)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_next(350, 9), on_next(400, 9), on_next(410, 10), on_next(490, 11), on_next(550, 12), on_next(560, 13)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return xs.sequenceEqual(ys)
    
#     results.messages.assert_equal(on_next(490, false), on_completed(490))
#     xs.subscriptions.assert_equal(subscribe(200, 490))
#     ys.subscriptions.assert_equal(subscribe(200, 490))


# def test_SequenceEqual_NotEqual_2_Sym():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_next(490, 8), on_next(520, 9), on_next(580, 10), on_next(600, 11)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(280, 4), on_next(300, 5), on_next(330, 6), on_next(340, 7), on_next(350, 9), on_next(400, 9), on_next(410, 10), on_next(490, 11), on_next(550, 12), on_next(560, 13)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return ys.sequenceEqual(xs)
    
#     results.messages.assert_equal(on_next(490, false), on_completed(490))
#     xs.subscriptions.assert_equal(subscribe(200, 490))
#     ys.subscriptions.assert_equal(subscribe(200, 490))


# def test_SequenceEqual_NotEqual_3():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_completed(330)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(400, 4), on_completed(420)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return xs.sequenceEqual(ys)
    
#     results.messages.assert_equal(on_next(420, false), on_completed(420))
#     xs.subscriptions.assert_equal(subscribe(200, 420))
#     ys.subscriptions.assert_equal(subscribe(200, 420))


# def test_SequenceEqual_NotEqual_3_Sym():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_completed(330)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(400, 4), on_completed(420)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return ys.sequenceEqual(xs)
    
#     results.messages.assert_equal(on_next(420, false), on_completed(420))
#     xs.subscriptions.assert_equal(subscribe(200, 420))
#     ys.subscriptions.assert_equal(subscribe(200, 420))


# def test_SequenceEqual_ComparerThrows():
#     var ex, msgs1, msgs2, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_completed(330)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(400, 4), on_completed(420)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return xs.sequenceEqual(ys, function (a, b) {
#             throw ex
        
    
#     results.messages.assert_equal(on_error(270, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 270))
#     ys.subscriptions.assert_equal(subscribe(200, 270))


# def test_SequenceEqual_ComparerThrows_Sym():
#     var ex, msgs1, msgs2, results, scheduler, xs, ys
#     ex = 'ex'
#     scheduler = TestScheduler()
#     msgs1 = [on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_completed(330)]
#     msgs2 = [on_next(90, 1), on_next(270, 3), on_next(400, 4), on_completed(420)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return ys.sequenceEqual(xs, function (a, b) {
#             throw ex
        
    
#     results.messages.assert_equal(on_error(270, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 270))
#     ys.subscriptions.assert_equal(subscribe(200, 270))


# def test_SequenceEqual_NotEqual_4():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(250, 1), on_completed(300)]
#     msgs2 = [on_next(290, 1), on_next(310, 2), on_completed(350)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return xs.sequenceEqual(ys)
    
#     results.messages.assert_equal(on_next(310, false), on_completed(310))
#     xs.subscriptions.assert_equal(subscribe(200, 310))
#     ys.subscriptions.assert_equal(subscribe(200, 310))


# def test_SequenceEqual_NotEqual_4_Sym():
#     var msgs1, msgs2, results, scheduler, xs, ys
#     scheduler = TestScheduler()
#     msgs1 = [on_next(250, 1), on_completed(300)]
#     msgs2 = [on_next(290, 1), on_next(310, 2), on_completed(350)]
#     xs = scheduler.create_hot_observable(msgs1)
#     ys = scheduler.create_hot_observable(msgs2)
#     results = scheduler.start(create=create)
#         return ys.sequenceEqual(xs)
    
#     results.messages.assert_equal(on_next(310, false), on_completed(310))
#     xs.subscriptions.assert_equal(subscribe(200, 310))
#     ys.subscriptions.assert_equal(subscribe(200, 310))


# def test_IsEmpty_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.isEmpty()
#     }).messages
#     res.assert_equal(on_next(250, true), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_IsEmpty_Return():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.isEmpty()
#     }).messages
#     res.assert_equal(on_next(210, false), on_completed(210))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_IsEmpty_Throw():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.isEmpty()
#     }).messages
#     res.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_IsEmpty_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1))
#     res = scheduler.start(create=create)
#         return xs.isEmpty()
#     }).messages
#     res.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))


# // SequenceEqual Array
# def test_SequenceEqual_Enumerable_Equal():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3, 4, 5, 6, 7])
    
#     res.messages.assert_equal(on_next(510, true), on_completed(510))
#     xs.subscriptions.assert_equal(subscribe(200, 510))


# def test_SequenceEqual_Enumerable_NotEqual_Elements():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3, 4, 9, 6, 7])
    
#     res.messages.assert_equal(on_next(310, false), on_completed(310))
#     xs.subscriptions.assert_equal(subscribe(200, 310))


# def test_SequenceEqual_Enumerable_Comparer_Equal():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3 - 2, 4, 5, 6 + 42, 7 - 6], function (x, y) {
#             return x % 2 == y % 2
        
    
#     res.messages.assert_equal(on_next(510, true), on_completed(510))
#     xs.subscriptions.assert_equal(subscribe(200, 510))


# def test_SequenceEqual_Enumerable_Comparer_NotEqual():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3 - 2, 4, 5 + 9, 6 + 42, 7 - 6], function (x, y) {
#             return x % 2 == y % 2
        
    
#     res.messages.assert_equal(on_next(310, false), on_completed(310))
#     xs.subscriptions.assert_equal(subscribe(200, 310))


# function throwComparer(value, exn) {
#     return function (x, y) {
#         if (x == value) {
#             throw exn
#         }
#         return x == y
#     }
# }

# def test_SequenceEqual_Enumerable_Comparer_Throws():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3, 4, 5, 6, 7], throwComparer(5, ex))
    
#     res.messages.assert_equal(on_error(310, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 310))


# def test_SequenceEqual_Enumerable_NotEqual_TooLong():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3, 4, 5, 6, 7, 8])
    
#     res.messages.assert_equal(on_next(510, false), on_completed(510))
#     xs.subscriptions.assert_equal(subscribe(200, 510))


# def test_SequenceEqual_Enumerable_NotEqual_TooShort():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3, 4, 5, 6])
    
#     res.messages.assert_equal(on_next(450, false), on_completed(450))
#     xs.subscriptions.assert_equal(subscribe(200, 450))


# def test_SequenceEqual_Enumerable_On_error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_error(310, ex))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3, 4])
    
#     res.messages.assert_equal(on_error(310, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 310))


# // ElementAt
# def test_ElementAt_First():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))
#     results = scheduler.start(create=create)
#         return xs.elementAt(0)
    
#     results.messages.assert_equal(on_next(280, 42), on_completed(280))
#     xs.subscriptions.assert_equal(subscribe(200, 280))


# def test_ElementAt_Other():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))
#     results = scheduler.start(create=create)
#         return xs.elementAt(2)
    
#     results.messages.assert_equal(on_next(470, 44), on_completed(470))
#     xs.subscriptions.assert_equal(subscribe(200, 470))


# def test_ElementAt_OutOfRange():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))
#     results = scheduler.start(create=create)
#         return xs.elementAt(3)
    
#     equal(1, results.messages.length)
#     equal(600, results.messages[0].time)
#     equal('E', results.messages[0].value.kind)
#     ok(results.messages[0].value.exception != null)


# def test_ElementAt_Error():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_error(420, ex))
#     results = scheduler.start(create=create)
#         return xs.elementAt(3)
    
#     results.messages.assert_equal(on_error(420, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 420))


# def test_ElementAtOrDefault_First():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))
#     results = scheduler.start(create=create)
#         return xs.elementAtOrDefault(0)
    
#     results.messages.assert_equal(on_next(280, 42), on_completed(280))
#     xs.subscriptions.assert_equal(subscribe(200, 280))


# def test_ElementAtOrDefault_Other():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))
#     results = scheduler.start(create=create)
#         return xs.elementAtOrDefault(2)
    
#     results.messages.assert_equal(on_next(470, 44), on_completed(470))
#     xs.subscriptions.assert_equal(subscribe(200, 470))


# def test_ElementAtOrDefault_OutOfRange():
#     var results, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_next(470, 44), on_completed(600))
#     results = scheduler.start(create=create)
#         return xs.elementAtOrDefault(3, 0)
    
#     results.messages.assert_equal(on_next(600, 0), on_completed(600))
#     xs.subscriptions.assert_equal(subscribe(200, 600))


# def test_ElementAtOrDefault_Error():
#     var ex, results, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(280, 42), on_next(360, 43), on_error(420, ex))
#     results = scheduler.start(create=create)
#         return xs.elementAtOrDefault(3)
    
#     results.messages.assert_equal(on_error(420, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 420))


# // First Async
# def test_FirstAsync_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.first()
    
#     res.messages.assert_equal(on_error(250, function (e) {
#         return e != null
#     }))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_FirstAsync_One():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.first()
    
#     res.messages.assert_equal(on_next(210, 2), on_completed(210))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_FirstAsync_Many():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.first()
    
#     res.messages.assert_equal(on_next(210, 2), on_completed(210))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_FirstAsync_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.first()
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_FirstAsync_Predicate():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.first(function (x) {
#             return x % 2 == 1
        
    
#     res.messages.assert_equal(on_next(220, 3), on_completed(220))
#     xs.subscriptions.assert_equal(subscribe(200, 220))


# def test_FirstAsync_Predicate_None():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.first(function (x) {
#             return x > 10
        
    
#     res.messages.assert_equal(on_error(250, function (e) {
#         return e != null
#     }))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_FirstAsync_Predicate_Throw():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_error(220, ex))
#     res = scheduler.start(create=create)
#         return xs.first(function (x) {
#             return x % 2 == 1
        
    
#     res.messages.assert_equal(on_error(220, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 220))


# def test_FirstAsync_PredicateThrows():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.first(function (x) {
#             if (x < 4) {
#                 return false
#             } else {
#                 throw ex
#             }
        
    
#     res.messages.assert_equal(on_error(230, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 230))


# // First or default
# def test_FirstOrDefaultAsync_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.firstOrDefault(null, 0)
    
#     res.messages.assert_equal(on_next(250, 0), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_FirstOrDefaultAsync_One():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.firstOrDefault(null, 0)
    
#     res.messages.assert_equal(on_next(210, 2), on_completed(210))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_FirstOrDefaultAsync_Many():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.firstOrDefault(null, 0)
    
#     res.messages.assert_equal(on_next(210, 2), on_completed(210))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_FirstOrDefaultAsync_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.firstOrDefault(null, 0)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_FirstOrDefaultAsync_Predicate():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.firstOrDefault(function (x) {
#             return x % 2 == 1
#         }, 0)
    
#     res.messages.assert_equal(on_next(220, 3), on_completed(220))
#     xs.subscriptions.assert_equal(subscribe(200, 220))


# def test_FirstOrDefaultAsync_Predicate_None():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.firstOrDefault(function (x) {
#             return x > 10
#         }, 0)
    
#     res.messages.assert_equal(on_next(250, 0), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_FirstOrDefaultAsync_Predicate_Throw():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_error(220, ex))
#     res = scheduler.start(create=create)
#         return xs.firstOrDefault(function (x) {
#             return x % 2 == 1
#         }, 0)
    
#     res.messages.assert_equal(on_error(220, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 220))


# def test_FirstOrDefaultAsync_PredicateThrows():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.firstOrDefault(function (x) {
#             if (x < 4) {
#                 return false
#             } else {
#                 throw ex
#             }
#         }, 0)
    
#     res.messages.assert_equal(on_error(230, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 230))


# // Last
# def test_LastAsync_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.last()
    
#     res.messages.assert_equal(on_error(250, function (e) {
#         return e != null
#     }))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_LastAsync_One():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.last()
    
#     res.messages.assert_equal(on_next(250, 2), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))

# def test_LastAsync_Many():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.last()
    
#     res.messages.assert_equal(on_next(250, 3), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_LastAsync_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.last()
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_LastAsync_Predicate():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.last(function (x) {
#             return x % 2 == 1
        
    
#     res.messages.assert_equal(on_next(250, 5), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_LastAsync_Predicate_None():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.last(function (x) {
#             return x > 10
        
    
#     res.messages.assert_equal(on_error(250, function (e) {
#         return e != null
#     }))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_LastAsync_Predicate_Throw():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.last(function (x) {
#             return x % 2 == 1
        
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_LastAsync_PredicateThrows():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.last(function (x) {
#             if (x < 4) {
#                 return x % 2 == 1
#             } else {
#                 throw ex
#             }
        
    
#     res.messages.assert_equal(on_error(230, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 230))


# // Last or Default
# def test_LastOrDefaultAsync_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.lastOrDefault(null, 0)
    
#     res.messages.assert_equal(on_next(250, 0), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_LastOrDefaultAsync_One():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.lastOrDefault(null, 0)
    
#     res.messages.assert_equal(on_next(250, 2), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_LastOrDefaultAsync_Many():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.lastOrDefault(null, 0)
    
#     res.messages.assert_equal(on_next(250, 3), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_LastOrDefaultAsync_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.lastOrDefault(null, 0)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_LastOrDefaultAsync_Predicate():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.lastOrDefault(function (x) {
#             return x % 2 == 1
#         }, 0)
    
#     res.messages.assert_equal(on_next(250, 5), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_LastOrDefaultAsync_Predicate_None():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.lastOrDefault(function (x) {
#             return x > 10
#         }, 0)
    
#     res.messages.assert_equal(on_next(250, 0), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_LastOrDefaultAsync_Predicate_Throw():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.lastOrDefault(function (x) {
#             return x > 10
#         }, 0)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_LastOrDefaultAsync_PredicateThrows():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.lastOrDefault(function (x) {
#             if (x < 4) {
#                 return x % 2 == 1
#             } else {
#                 throw ex
#             }
#         }, 0)
    
#     res.messages.assert_equal(on_error(230, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 230))


# // Single
# def test_SingleAsync_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.single()
    
#     res.messages.assert_equal(on_error(250, function (e) {
#         return e != null
#     }))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_SingleAsync_One():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.single()
    
#     res.messages.assert_equal(on_next(250, 2), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_SingleAsync_Many():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.single()
    
#     res.messages.assert_equal(on_error(220, function (e) {
#         return e != null
#     }))
#     xs.subscriptions.assert_equal(subscribe(200, 220))


# def test_SingleAsync_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.single()
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_SingleAsync_Predicate():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.single(function (x) {
#             return x % 2 == 1
        
    
#     res.messages.assert_equal(on_error(240, function (e) {
#         return e != null
#     }))
#     xs.subscriptions.assert_equal(subscribe(200, 240))


# def test_SingleAsync_Predicate_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.single(function (x) {
#             return x % 2 == 1
        
    
#     res.messages.assert_equal(on_error(250, function (e) {
#         return e != null
#     }))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_SingleAsync_Predicate_One():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.single(function (x) {
#             return x == 4
        
    
#     res.messages.assert_equal(on_next(250, 4), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_SingleAsync_Predicate_Throw():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.single(function (x) {
#             return x > 10
        
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_SingleAsync_PredicateThrows():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.single(function (x) {
#             if (x < 4) {
#                 return false
#             } else {
#                 throw ex
#             }
        
    
#     res.messages.assert_equal(on_error(230, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 230))


# // Single Or Default
# def test_SingleOrDefaultAsync_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.singleOrDefault(null, 0)
    
#     res.messages.assert_equal(on_next(250, 0), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_SingleOrDefaultAsync_One():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.singleOrDefault(null, 0)
    
#     res.messages.assert_equal(on_next(250, 2), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_SingleOrDefaultAsync_Many():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.singleOrDefault(null, 0)
    
#     res.messages.assert_equal(on_error(220, function (e) {
#         return e != null
#     }))
#     xs.subscriptions.assert_equal(subscribe(200, 220))


# def test_SingleOrDefaultAsync_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.singleOrDefault(null, 0)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_SingleOrDefaultAsync_Predicate():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.singleOrDefault(function (x) {
#             return x % 2 == 1
#         }, 0)
    
#     res.messages.assert_equal(on_error(240, function (e) {
#         return e != null
#     }))
#     xs.subscriptions.assert_equal(subscribe(200, 240))


# def test_SingleOrDefaultAsync_Predicate_Empty():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.singleOrDefault(function (x) {
#             return x % 2 == 1
#         }, 0)
    
#     res.messages.assert_equal(on_next(250, 0), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_SingleOrDefaultAsync_Predicate_One():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.singleOrDefault(function (x) {
#             return x == 4
#         }, 0)
    
#     res.messages.assert_equal(on_next(250, 4), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_SingleOrDefaultAsync_Predicate_None():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.singleOrDefault(function (x) {
#             return x > 10
#         }, 0)
    
#     res.messages.assert_equal(on_next(250, 0), on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))


# def test_SingleOrDefaultAsync_Predicate_Throw():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_error(210, ex))
#     res = scheduler.start(create=create)
#         return xs.singleOrDefault(function (x) {
#             return x > 10
#         }, 0)
    
#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))


# def test_SingleOrDefaultAsync_PredicateThrows():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(150, 1), on_next(210, 2), on_next(220, 3), on_next(230, 4), on_next(240, 5), on_completed(250))
#     res = scheduler.start(create=create)
#         return xs.singleOrDefault(function (x) {
#             if (x < 4) {
#                 return false
#             } else {
#                 throw ex
#             }
#         }, 0)
    
#     res.messages.assert_equal(on_error(230, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

if __name__ == '__main__':
    test_count_empty()