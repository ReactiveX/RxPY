import logging

from rx.testing import ReactiveTest

FORMAT = '%(asctime)-15s %(threadName)s %(message)s'
logging.basicConfig(filename='rx.log', format=FORMAT, level=logging.DEBUG)
log = logging.getLogger('Rx')

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class RxException(Exception):
    pass


# Helper function for raising exceptions within lambdas
def _raise(ex):
    raise RxException(ex)



# // TakeLastBuffer
# def test_takeLastBuffer_with_time_Zero1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(0, scheduler)

#     res.messages.assert_equal(send(230, function (lst) {
#         return lst.length === 0
#     }), close(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_takeLastBuffer_with_time_Zero2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), close(230))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(0, scheduler)

#     res.messages.assert_equal(send(230, function (lst) {
#         return lst.length === 0
#     }), close(230))
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
#     xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), close(240))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(25, scheduler)

#     res.messages.assert_equal(send(240, function (lst) {
#         return arrayEqual(lst, [2, 3])
#     }), close(240))
#     xs.subscriptions.assert_equal(subscribe(200, 240))

# def test_takeLastBuffer_with_time_Some2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), close(300))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(25, scheduler)

#     res.messages.assert_equal(send(300, function (lst) {
#         return lst.length === 0
#     }), close(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))

# def test_takeLastBuffer_with_time_Some3():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), send(240, 4), send(250, 5), send(260, 6), send(270, 7), send(280, 8), send(290, 9), close(300))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(45, scheduler)

#     res.messages.assert_equal(send(300, function (lst) {
#         return arrayEqual(lst, [6, 7, 8, 9])
#     }), close(300))
#     xs.subscriptions.assert_equal(subscribe(200, 300))

# def test_takeLastBuffer_with_time_Some4():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(210, 1), send(240, 2), send(250, 3), send(280, 4), send(290, 5), send(300, 6), close(350))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(25, scheduler)

#     res.messages.assert_equal(send(350, function (lst) {
#         return lst.length === 0
#     }), close(350))
#     xs.subscriptions.assert_equal(subscribe(200, 350))

# def test_takeLastBuffer_with_time_All():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(50, scheduler)

#     res.messages.assert_equal(send(230, function (lst) {
#         return arrayEqual(lst, [1, 2])
#     }), close(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_takeLastBuffer_with_time_Error():
#     var ex, res, scheduler, xs
#     scheduler = TestScheduler()
#     ex = 'ex'
#     xs = scheduler.create_hot_observable(throw(210, ex))
#     res = scheduler.start(create)
#         return xs.takeLastBuffer_with_time(50, scheduler)

#     res.messages.assert_equal(throw(210, ex))
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
#     xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))
#     res = scheduler.start(create)
#         return xs.takeWithTime(0, scheduler)

#     res.messages.assert_equal(close(201))
#     xs.subscriptions.assert_equal(subscribe(200, 201))

# def test_Take_Some():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), close(240))
#     res = scheduler.start(create)
#         return xs.takeWithTime(25, scheduler)

#     res.messages.assert_equal(send(210, 1), send(220, 2), close(225))
#     xs.subscriptions.assert_equal(subscribe(200, 225))

# def test_Take_Late():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), close(230))
#     res = scheduler.start(create)
#         return xs.takeWithTime(50, scheduler)

#     res.messages.assert_equal(send(210, 1), send(220, 2), close(230))
#     xs.subscriptions.assert_equal(subscribe(200, 230))

# def test_Take_Error():
#     var ex, res, scheduler, xs
#     scheduler = TestScheduler()
#     ex = 'ex'
#     xs = scheduler.create_hot_observable(throw(210, ex))
#     res = scheduler.start(create)
#         return xs.takeWithTime(50, scheduler)

#     res.messages.assert_equal(throw(210, ex))
#     xs.subscriptions.assert_equal(subscribe(200, 210))

# def test_Take_Never():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable()
#     res = scheduler.start(create)
#         return xs.takeWithTime(50, scheduler)

#     res.messages.assert_equal(close(250))
#     xs.subscriptions.assert_equal(subscribe(200, 250))

# def test_Take_Twice1():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), send(240, 4), send(250, 5), send(260, 6), close(270))
#     res = scheduler.start(create)
#         return xs.takeWithTime(55, scheduler).takeWithTime(35, scheduler)

#     res.messages.assert_equal(send(210, 1), send(220, 2), send(230, 3), close(235))
#     xs.subscriptions.assert_equal(subscribe(200, 235))

# def test_Take_Twice2():
#     var res, scheduler, xs
#     scheduler = TestScheduler()
#     xs = scheduler.create_hot_observable(send(210, 1), send(220, 2), send(230, 3), send(240, 4), send(250, 5), send(260, 6), close(270))
#     res = scheduler.start(create)
#         return xs.takeWithTime(35, scheduler).takeWithTime(55, scheduler)

#     res.messages.assert_equal(send(210, 1), send(220, 2), send(230, 3), close(235))
#     xs.subscriptions.assert_equal(subscribe(200, 235))




# // TakeLast


if __name__ == '__main__':
    test_buffer_with_time_or_count_basic()
