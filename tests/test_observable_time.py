import logging
from datetime import datetime, timedelta

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest, is_prime, MockDisposable
from rx.disposables import Disposable, SerialDisposable

FORMAT = '%(asctime)-15s %(threadName)s %(message)s'
logging.basicConfig(filename='rx.log', format=FORMAT, level=logging.DEBUG)
#logging.basicConfig(format=FORMAT, level=logging.DEBUG)
log = logging.getLogger('Rx')

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

def test_window_with_time_or_count_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_completed(600))

    def create():
        def projection(w, i):
            def inner_proj(x):
                log.info("%s %s" % (i, x))
                return "%s %s" % (i, x)
            return w.select(inner_proj)
        return xs.window_with_time_or_count(70, 3, scheduler).select(projection).merge_observable()

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(205, "0 1"), on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "1 4"), on_next(320, "2 5"), on_next(350, "2 6"), on_next(370, "2 7"), on_next(420, "3 8"), on_next(470, "4 9"), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_window_with_time_or_count_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_error(600, ex))

    def create():
        def projection(w, i):
            def inner_proj(x):
                return "%s %s" % (i, x)
            return w.select(inner_proj)
        return xs.window_with_time_or_count(70, 3, scheduler).select(projection).merge_observable()

    results = scheduler.start(create)

    results.messages.assert_equal(on_next(205, "0 1"), on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "1 4"), on_next(320, "2 5"), on_next(350, "2 6"), on_next(370, "2 7"), on_next(420, "3 8"), on_next(470, "4 9"), on_error(600, ex))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_window_with_time_or_count_disposed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_completed(600))

    def create():
        def projection(w, i):
            def inner_proj(x):
                return "%s %s" % (i, x)
            return w.select(inner_proj)
        return xs.window_with_time_or_count(70, 3, scheduler).select(projection).merge_observable()

    results = scheduler.start(create, disposed=370)
    results.messages.assert_equal(on_next(205, "0 1"), on_next(210, "0 2"), on_next(240, "0 3"), on_next(280, "1 4"), on_next(320, "2 5"), on_next(350, "2 6"), on_next(370, "2 7"))
    xs.subscriptions.assert_equal(subscribe(200, 370))

def test_buffer_with_time_or_count_basic():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_completed(600))

    def create():
        return xs.buffer_with_time_or_count(70, 3, scheduler).select(lambda x: ",".join([str(a) for a in x]))

    results = scheduler.start(create)

    results.messages.assert_equal(on_next(240, "1,2,3"), on_next(310, "4"), on_next(370, "5,6,7"), on_next(440, "8"), on_next(510, "9"), on_next(580, ""), on_next(600, ""), on_completed(600))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_buffer_with_time_or_count_error():
    ex = 'ex'
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_error(600, ex))

    def create():
        return xs.buffer_with_time_or_count(70, 3, scheduler).select(lambda x: ",".join([str(a) for a in x]))

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(240, "1,2,3"), on_next(310, "4"), on_next(370, "5,6,7"), on_next(440, "8"), on_next(510, "9"), on_next(580, ""), on_error(600, ex))
    xs.subscriptions.assert_equal(subscribe(200, 600))

def test_buffer_with_time_or_count_disposed():
    scheduler = TestScheduler()
    xs = scheduler.create_hot_observable(on_next(205, 1), on_next(210, 2), on_next(240, 3), on_next(280, 4), on_next(320, 5), on_next(350, 6), on_next(370, 7), on_next(420, 8), on_next(470, 9), on_completed(600))

    def create():
        return xs.buffer_with_time_or_count(70, 3, scheduler).select(lambda x: ",".join([str(a) for a in x]))

    results = scheduler.start(create, disposed=370)
    results.messages.assert_equal(on_next(240, "1,2,3"), on_next(310, "4"), on_next(370, "5,6,7"))
    xs.subscriptions.assert_equal(subscribe(200, 370))

def test_generate_timespan_finite():
    scheduler = TestScheduler()

    def create():
        return Observable.generate_with_relative_time(0,
            lambda x: x <= 3,
            lambda x: x + 1,
            lambda x: x,
            lambda x: x + 1,
            scheduler=scheduler)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2), on_next(211, 3), on_completed(211))

def test_generate_timespan_throw_condition():
    ex = 'ex'
    scheduler = TestScheduler()

    def create():
        return Observable.generate_with_relative_time(0,
            lambda x: _raise(ex),
            lambda x: x + 1,
            lambda x: x,
            lambda x: x + 1,
            scheduler=scheduler)

    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_generate_timespan_throw_result_selector():
    ex = 'ex'
    scheduler = TestScheduler()

    def create():
        return Observable.generate_with_relative_time(0,
            lambda x: True,
            lambda x: x + 1,
            lambda x: _raise(ex),
            lambda x: x + 1,
            scheduler=scheduler)

    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_generate_timespan_throw_iterate():
    ex = 'ex'
    scheduler = TestScheduler()

    def create():
        return Observable.generate_with_relative_time(0,
            lambda x: True,
            lambda x: _raise(ex),
            lambda x: x,
            lambda x: x + 1,
            scheduler=scheduler)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(202, 0), on_error(202, ex))

def test_generate_timespan_throw_timeselector():
    ex = 'ex'
    scheduler = TestScheduler()

    def create():
        return Observable.generate_with_relative_time(0,
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: _raise(ex),
            scheduler=scheduler)

    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_generate_timespan_Dispose():
    scheduler = TestScheduler()

    def create():
        return Observable.generate_with_relative_time(0,
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: x + 1,
            scheduler=scheduler)

    results = scheduler.start(create, disposed=210)
    results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2))

def test_generate_datetime_offset_finite():
    scheduler = TestScheduler()

    return Observable.generate_with_relative_time(0,
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: scheduler.now() + x + 1,
            scheduler=scheduler)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2), on_next(211, 3), on_completed(211))

def test_generate_datetime_offset_throw_condition():
    ex = 'ex'
    scheduler = TestScheduler()
    return Observable.generate_with_relative_time(0,
            lambda x: _raise(ex),
            lambda x: x + 1,
            lambda x: x,
            lambda x: scheduler.now() + x + 1,
            scheduler=scheduler)

    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_generate_datetime_offset_throw_result_selector():
    ex = 'ex'
    scheduler = TestScheduler()

    return Observable.generate_with_relative_time(0,
            lambda x: True,
            lambda x: x + 1,
            lambda x: _raise(ex),
            lambda x: scheduler.now() + x + 1,
            scheduler=scheduler)

    results = scheduler.start(create)
    results.messages.assert_equal(on_error(201, ex))

def test_generate_datetime_offset_throw_iterate():
    ex = 'ex'
    scheduler = TestScheduler()

    return Observable.generate_with_relative_time(0,
            lambda x: True,
            lambda x: _raise(ex),
            lambda x: x,
            lambda x: scheduler.now() + x + 1,
            scheduler=scheduler)

    results = scheduler.start(create)
    results.messages.assert_equal(on_next(202, 0), on_error(202, ex))

def test_generate_datetime_offset_throw_time_selector():
    ex = 'ex'
    scheduler = TestScheduler()

    return Observable.generate_with_relative_time(0,
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: _raise(ex),
            scheduler=scheduler)

    results.messages.assert_equal(on_error(201, ex))

def test_generate_datetime_offset_dispose():
    scheduler = TestScheduler()

    return Observable.generate_with_relative_time(0,
            lambda x: True,
            lambda x: x + 1,
            lambda x: x,
            lambda x: scheduler.now() + x + 1,
            scheduler=scheduler)

    results = scheduler.start(create, disposed=210)
    results.messages.assert_equal(on_next(202, 0), on_next(204, 1), on_next(207, 2))




# // TakeLastBuffer
# def test_takeLastBuffer_with_time_Zero1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(0, scheduler)

#     res.messages.assert_equal(on_next(230, function (lst) {
#         return lst.length === 0
#     }), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_takeLastBuffer_with_time_Zero2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(0, scheduler)

#     res.messages.assert_equal(on_next(230, function (lst) {
#         return lst.length === 0
#     }), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))


# function arrayEqual(arr1, arr2) {
#     if (arr1.length != arr2.length) return false
#     for (var i = 0, len = arr1.length i < len i++) {
#         if (arr1[i] != arr2[i]) return false
#     }
#     return true
# }

# def test_takeLastBuffer_with_time_Some1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(25, scheduler)

#     res.messages.assert_equal(on_next(240, function (lst) {
#         return arrayEqual(lst, [2, 3])
#     }), on_completed(240))
#     xs.subscriptions.assert_equal(subscribe(200, 240))

# def test_takeLastBuffer_with_time_Some2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(25, scheduler)

#     res.messages.assert_equal(on_next(300, function (lst) {
#         return lst.length === 0
#     }), on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))

# def test_takeLastBuffer_with_time_Some3():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_next(270, 7), on_next(280, 8), on_next(290, 9), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(45, scheduler)

#     res.messages.assert_equal(on_next(300, function (lst) {
#         return arrayEqual(lst, [6, 7, 8, 9])
#     }), on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))

# def test_takeLastBuffer_with_time_Some4():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(250, 3), on_next(280, 4), on_next(290, 5), on_next(300, 6), on_completed(350))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(25, scheduler)

#     res.messages.assert_equal(on_next(350, function (lst) {
#         return lst.length === 0
#     }), on_completed(350))
#     xs.subscriptions.assert_equal(subscribe(200, 350))

# def test_takeLastBuffer_with_time_All():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(50, scheduler)

#     res.messages.assert_equal(on_next(230, function (lst) {
#         return arrayEqual(lst, [1, 2])
#     }), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_takeLastBuffer_with_time_Error():
#     var ex, res, scheduler, xs
#     scheduler = TestScheduler()
#     ex = 'ex'
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(50, scheduler)

#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_takeLastBuffer_with_time_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(50, scheduler)

#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_Take_Zero():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeWithTime(0, scheduler)

#     res.messages.assert_equal(on_completed(201))
#     xs.subscriptions.assert_equal(subscribe(200, 201))

# def test_Take_Some():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240))
#     res = scheduler.start(create)
#         return xs.takeWithTime(25, scheduler)

#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_completed(225))
#     xs.subscriptions.assert_equal(subscribe(200, 225))

# def test_Take_Late():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeWithTime(50, scheduler)

#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_Take_Error():
#     var ex, res, scheduler, xs
#     scheduler = TestScheduler()
#     ex = 'ex'
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.takeWithTime(50, scheduler)

#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_Take_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.takeWithTime(50, scheduler)

#     res.messages.assert_equal(on_completed(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))

# def test_Take_Twice1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.takeWithTime(55, scheduler).takeWithTime(35, scheduler)

#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(235))
#     xs.subscriptions.assert_equal(subscribe(200, 235))

# def test_Take_Twice2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.takeWithTime(35, scheduler).takeWithTime(55, scheduler)

#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(235))
#     xs.subscriptions.assert_equal(subscribe(200, 235))




# // TakeLast
# def test_TakeLast_Zero1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(0, scheduler)

#     res.messages.assert_equal(on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_TakeLast_Zero1_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(0, scheduler, scheduler)

#     res.messages.assert_equal(on_completed(231))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_TakeLast_Zero2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(0, scheduler)

#     res.messages.assert_equal(on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_TakeLast_Zero2_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(0, scheduler, scheduler)

#     res.messages.assert_equal(on_completed(231))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_TakeLast_Some1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler)

#     res.messages.assert_equal(on_next(240, 2), on_next(240, 3), on_completed(240))
#     xs.subscriptions.assert_equal(subscribe(200, 240))


# def test_TakeLast_Some1_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(240))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler, scheduler)

#     res.messages.assert_equal(on_next(241, 2), on_next(242, 3), on_completed(243))
#     xs.subscriptions.assert_equal(subscribe(200, 240))

# def test_TakeLast_Some2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler)

#     res.messages.assert_equal(on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))


# def test_TakeLast_Some2_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler, scheduler)

#     res.messages.assert_equal(on_completed(301))
#     xs.subscriptions.assert_equal(subscribe(200, 300))


# def test_TakeLast_Some3():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_next(270, 7), on_next(280, 8), on_next(290, 9), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(45, scheduler)

#     res.messages.assert_equal(on_next(300, 6), on_next(300, 7), on_next(300, 8), on_next(300, 9), on_completed(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))

# def test_TakeLast_Some3_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_next(270, 7), on_next(280, 8), on_next(290, 9), on_completed(300))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(45, scheduler, scheduler)

#     res.messages.assert_equal(on_next(301, 6), on_next(302, 7), on_next(303, 8), on_next(304, 9), on_completed(305))
#     xs.subscriptions.assert_equal(subscribe(200, 300))

# def test_TakeLast_Some4():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(250, 3), on_next(280, 4), on_next(290, 5), on_next(300, 6), on_completed(350))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler)

#     res.messages.assert_equal(on_completed(350))
#     xs.subscriptions.assert_equal(subscribe(200, 350))

# def test_TakeLast_Some4_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(240, 2), on_next(250, 3), on_next(280, 4), on_next(290, 5), on_next(300, 6), on_completed(350))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(25, scheduler, scheduler)

#     res.messages.assert_equal(on_completed(351))
#     xs.subscriptions.assert_equal(subscribe(200, 350))

# def test_TakeLast_All():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler)

#     res.messages.assert_equal(on_next(230, 1), on_next(230, 2), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))


# def test_TakeLast_All_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler, scheduler)

#     res.messages.assert_equal(on_next(231, 1), on_next(232, 2), on_completed(233))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_TakeLast_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler)

#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_TakeLast_Error_WithLoopScheduler():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler, scheduler)

#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_TakeLast_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler)

#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_TakeLast_Never_WithLoopScheduler():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.takeLastWithTime(50, scheduler, scheduler)

#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))




# // SkipUntil
# def test_SkipUntil_Zero():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(0), scheduler)

#     res.messages.assert_equal(on_next(210, 1), on_next(220, 2), on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_SkipUntil_Late():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_completed(230))
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(250), scheduler)

#     res.messages.assert_equal(on_completed(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_SkipUntil_Error():
#     var ex, res, scheduler, xs
#     ex = 'ex'
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_error(210, ex))
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(250), scheduler)

#     res.messages.assert_equal(on_error(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_SkipUntil_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(250), scheduler)

#     res.messages.assert_equal()
#     xs.subscriptions.assert_equal(subscribe(200, 1000))

# def test_SkipUntil_Twice1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(215), scheduler).skipUntilWithTime(Date(230), scheduler)

#     res.messages.assert_equal(on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     xs.subscriptions.assert_equal(subscribe(200, 270))

# def test_SkipUntil_Twice2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(on_next(210, 1), on_next(220, 2), on_next(230, 3), on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     res = scheduler.start(create)
#         return xs.skipUntilWithTime(Date(230), scheduler).skipUntilWithTime(Date(215), scheduler)

#     res.messages.assert_equal(on_next(240, 4), on_next(250, 5), on_next(260, 6), on_completed(270))
#     xs.subscriptions.assert_equal(subscribe(200, 270))



if __name__ == '__main__':
    test_buffer_with_time_or_count_basic()
