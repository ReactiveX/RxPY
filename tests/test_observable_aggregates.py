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



# // SequenceEqual Array
# def test_SequenceEqual_Enumerable_Equal():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3, 4, 5, 6, 7])
    
#     res.messages.assert_equal(on_next(510, True), on_completed(510))
#     xs.subscriptions.assert_equal(subscribe(200, 510))


# def test_SequenceEqual_Enumerable_NotEqual_Elements():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3, 4, 9, 6, 7])
    
#     res.messages.assert_equal(on_next(310, False), on_completed(310))
#     xs.subscriptions.assert_equal(subscribe(200, 310))


# def test_SequenceEqual_Enumerable_Comparer_Equal():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3 - 2, 4, 5, 6 + 42, 7 - 6], function (x, y) {
#             return x % 2 == y % 2
        
    
#     res.messages.assert_equal(on_next(510, True), on_completed(510))
#     xs.subscriptions.assert_equal(subscribe(200, 510))


# def test_SequenceEqual_Enumerable_Comparer_NotEqual():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3 - 2, 4, 5 + 9, 6 + 42, 7 - 6], function (x, y) {
#             return x % 2 == y % 2
        
    
#     res.messages.assert_equal(on_next(310, False), on_completed(310))
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
    
#     res.messages.assert_equal(on_next(510, False), on_completed(510))
#     xs.subscriptions.assert_equal(subscribe(200, 510))


# def test_SequenceEqual_Enumerable_NotEqual_TooShort():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(110, 1), on_next(190, 2), on_next(240, 3), on_next(290, 4), on_next(310, 5), on_next(340, 6), on_next(450, 7), on_completed(510))
#     res = scheduler.start(create=create)
#         return xs.sequenceEqual([3, 4, 5, 6])
    
#     res.messages.assert_equal(on_next(450, False), on_completed(450))
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
#                 return False
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
#                 return False
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
#                 return False
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
#                 return False
#             } else {
#                 throw ex
#             }
#         }, 0)
    
#     res.messages.assert_equal(on_error(230, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

if __name__ == '__main__':
    test_count_empty()