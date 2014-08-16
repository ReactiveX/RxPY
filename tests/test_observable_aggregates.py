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


if __name__ == '__main__':
    test_count_empty()