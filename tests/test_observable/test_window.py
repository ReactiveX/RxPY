import unittest
from datetime import timedelta

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

class TestWindow(unittest.TestCase):

    def test_window_closings_basic(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        window = [1]
    
        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return Observable.timer(curr * 100, scheduler=scheduler)
            
            def selector(w, i):
                return w.select(lambda x: str(i) + ' ' + str(x))
        
            return xs.window(closing_selector=closing).select(selector).merge_observable()
    
        results = scheduler.start(create=create)
        results.messages.assert_equal(on_next(250, "0 3"), on_next(260, "0 4"), on_next(310, "1 5"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(420, "1 8"), on_next(470, "1 9"), on_next(550, "2 10"), on_completed(590))
        xs.subscriptions.assert_equal(subscribe(200, 590))

    def test_window_closings_dispose(self):
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        window = [1]
    
        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return Observable.timer(curr * 100, scheduler=scheduler)
        
            def selector(w, i):
                return w.select(lambda x: str(i) + ' ' + str(x))
            
            return xs.window(closing_selector=closing).select(selector).merge_observable()

        results = scheduler.start(create=create, disposed=400)
     
        results.messages.assert_equal(on_next(250, "0 3"), on_next(260, "0 4"), on_next(310, "1 5"), on_next(340, "1 6"))
        xs.subscriptions.assert_equal(subscribe(200, 400))


    def test_window_closings_error(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_error(590, ex))
        window = [1]

        def create():
            def closing():
                curr = window[0]
                window[0] += 1
                return Observable.timer(curr * 100, scheduler=scheduler)
        
            def selector(w, i):
                return w.select(lambda x: str(i) + ' ' + str(x))
            
            return xs.window(closing_selector=closing).select(selector).merge_observable()

        results = scheduler.start(create=create)
    
        results.messages.assert_equal(on_next(250, "0 3"), on_next(260, "0 4"), on_next(310, "1 5"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(420, "1 8"), on_next(470, "1 9"), on_next(550, "2 10"), on_error(590, ex))
        xs.subscriptions.assert_equal(subscribe(200, 590))

    def test_window_closings_throw(self):
        ex = 'ex'
        scheduler = TestScheduler()
        xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
        window = [1]

        def create():
            def closing():
                raise Exception(ex)
        
            def selector(w, i):
                return w.select(lambda x: str(i) + ' ' + str(x))
            
            return xs.window(closing_selector=closing).select(selector).merge_observable()

        results = scheduler.start(create=create)

        results.messages.assert_equal(on_error(200, ex))
        xs.subscriptions.assert_equal(subscribe(200, 200))

    # def test_Window_Closings_WindowClose_Error():
    #     var ex, results, scheduler, window, xs
    #     ex = 'ex'
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
    #     window = 1
    #     results = scheduler.startWithCreate(function () {
    #         return xs.window(function () {
    #             return Observable.throwException(ex, scheduler)
    #         }).select(function (w, i) {
    #             return w.select(function (x) {
    #                 return i.toString() + ' ' + x.toString()
    #             })
    #         }).mergeObservable()
    #     })
    #     results.messages.assert_equal(on_error(201, ex))
    #     xs.subscriptions.assert_equal(subscribe(200, 201))
    # })

    # def test_Window_Closings_Default():
    #     var results, scheduler, window, xs
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
    #     window = 1
    #     results = scheduler.startWithCreate(function () {
    #         return xs.window(function () {
    #             return Observable.timer(window++ * 100, undefined, scheduler)
    #         }).select(function (w, i) {
    #             return w.select(function (x) {
    #                 return i.toString() + ' ' + x.toString()
    #             })
    #         }).mergeObservable()
    #     })
    #     results.messages.assert_equal(on_next(250, "0 3"), on_next(260, "0 4"), on_next(310, "1 5"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(420, "1 8"), on_next(470, "1 9"), on_next(550, "2 10"), on_completed(590))
    #     xs.subscriptions.assert_equal(subscribe(200, 590))
    # })

    # def test_Window_OpeningClosings_Basic():
    #     var results, scheduler, xs, ys
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
    #     ys = scheduler.create_hot_observable(on_next(255, 50), on_next(330, 100), on_next(350, 50), on_next(400, 90), on_completed(900))
    #     results = scheduler.startWithCreate(function () {
    #         return xs.window(ys, function (x) {
    #             return Observable.timer(x, undefined, scheduler)
    #         }).select(function (w, i) {
    #             return w.select(function (x) {
    #                 return i.toString() + ' ' + x.toString()
    #             })
    #         }).mergeObservable()
    #     })
    #     results.messages.assert_equal(on_next(260, "0 4"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(410, "3 7"), on_next(420, "1 8"), on_next(420, "3 8"), on_next(470, "3 9"), on_completed(900))
    #     xs.subscriptions.assert_equal(subscribe(200, 900))
    #     ys.subscriptions.assert_equal(subscribe(200, 900))
    # })

    # def test_Window_OpeningClosings_Throw():
    #     var ex, results, scheduler, xs, ys
    #     ex = 'ex'
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
    #     ys = scheduler.create_hot_observable(on_next(255, 50), on_next(330, 100), on_next(350, 50), on_next(400, 90), on_completed(900))
    #     results = scheduler.startWithCreate(function () {
    #         return xs.window(ys, function (x) {
    #             throw ex
    #         }).select(function (w, i) {
    #             return w.select(function (x) {
    #                 return i.toString() + ' ' + x.toString()
    #             })
    #         }).mergeObservable()
    #     })
    #     results.messages.assert_equal(on_error(255, ex))
    #     xs.subscriptions.assert_equal(subscribe(200, 255))
    #     ys.subscriptions.assert_equal(subscribe(200, 255))
    # })

    # def test_Window_OpeningClosings_Dispose():
    #     var results, scheduler, xs, ys
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
    #     ys = scheduler.create_hot_observable(on_next(255, 50), on_next(330, 100), on_next(350, 50), on_next(400, 90), on_completed(900))
    #     results = scheduler.startWithDispose(function () {
    #         return xs.window(ys, function (x) {
    #             return Observable.timer(x, undefined, scheduler)
    #         }).select(function (w, i) {
    #             return w.select(function (x) {
    #                 return i.toString() + ' ' + x.toString()
    #             })
    #         }).mergeObservable()
    #     }, 415)
    #     results.messages.assert_equal(on_next(260, "0 4"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(410, "3 7"))
    #     xs.subscriptions.assert_equal(subscribe(200, 415))
    #     ys.subscriptions.assert_equal(subscribe(200, 415))
    # })

    # def test_Window_OpeningClosings_Data_Error():
    #     var ex, results, scheduler, xs, ys
    #     ex = 'ex'
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_error(415, ex))
    #     ys = scheduler.create_hot_observable(on_next(255, 50), on_next(330, 100), on_next(350, 50), on_next(400, 90), on_completed(900))
    #     results = scheduler.startWithCreate(function () {
    #         return xs.window(ys, function (x) {
    #             return Observable.timer(x, undefined, scheduler)
    #         }).select(function (w, i) {
    #             return w.select(function (x) {
    #                 return i.toString() + ' ' + x.toString()
    #             })
    #         }).mergeObservable()
    #     })
    #     results.messages.assert_equal(on_next(260, "0 4"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(410, "3 7"), on_error(415, ex))
    #     xs.subscriptions.assert_equal(subscribe(200, 415))
    #     ys.subscriptions.assert_equal(subscribe(200, 415))
    # })

    # def test_Window_OpeningClosings_Window_Error():
    #     var ex, results, scheduler, xs, ys
    #     ex = 'ex'
    #     scheduler = TestScheduler()
    #     xs = scheduler.create_hot_observable(on_next(90, 1), on_next(180, 2), on_next(250, 3), on_next(260, 4), on_next(310, 5), on_next(340, 6), on_next(410, 7), on_next(420, 8), on_next(470, 9), on_next(550, 10), on_completed(590))
    #     ys = scheduler.create_hot_observable(on_next(255, 50), on_next(330, 100), on_next(350, 50), on_next(400, 90), on_error(415, ex))
    #     results = scheduler.startWithCreate(function () {
    #         return xs.window(ys, function (x) {
    #             return Observable.timer(x, undefined, scheduler)
    #         }).select(function (w, i) {
    #             return w.select(function (x) {
    #                 return i.toString() + ' ' + x.toString()
    #             })
    #         }).mergeObservable()
    #     })
    #     results.messages.assert_equal(on_next(260, "0 4"), on_next(340, "1 6"), on_next(410, "1 7"), on_next(410, "3 7"), on_error(415, ex))
    #     xs.subscriptions.assert_equal(subscribe(200, 415))
    #     ys.subscriptions.assert_equal(subscribe(200, 415))
    # })

    # def test_Window_Boundaries_Simple():
    #     var scheduler = TestScheduler()

    #     var xs = scheduler.create_hot_observable(
    #         on_next(90, 1),
    #         on_next(180, 2),
    #         on_next(250, 3),
    #         on_next(260, 4),
    #         on_next(310, 5),
    #         on_next(340, 6),
    #         on_next(410, 7),
    #         on_next(420, 8),
    #         on_next(470, 9),
    #         on_next(550, 10),
    #         on_completed(590)
    #     )

    #     var ys = scheduler.create_hot_observable(
    #         on_next(255, true),
    #         on_next(330, true),
    #         on_next(350, true),
    #         on_next(400, true),
    #         on_next(500, true),
    #         on_completed(900)
    #     )

    #     var res = scheduler.startWithCreate(function () {
    #         return xs.window(ys).select(function (w, i) {
    #             return w.select(function (x) {
    #                 return i.toString() + ' ' + x.toString()
    #             })
    #         }).mergeObservable()
    #     })

    #     res.messages.assert_equal(
    #         on_next(250, "0 3"),
    #         on_next(260, "1 4"),
    #         on_next(310, "1 5"),
    #         on_next(340, "2 6"),
    #         on_next(410, "4 7"),
    #         on_next(420, "4 8"),
    #         on_next(470, "4 9"),
    #         on_next(550, "5 10"),
    #         on_completed(590)
    #     )

    #     xs.subscriptions.assert_equal(
    #         subscribe(200, 590)
    #     )

    #     ys.subscriptions.assert_equal(
    #         subscribe(200, 590)
    #     )
    # })

    # def test_Window_Boundaries_on_completedBoundaries():
    #     var scheduler = TestScheduler()

    #     var xs = scheduler.create_hot_observable(
    #             on_next(90, 1),
    #             on_next(180, 2),
    #             on_next(250, 3),
    #             on_next(260, 4),
    #             on_next(310, 5),
    #             on_next(340, 6),
    #             on_next(410, 7),
    #             on_next(420, 8),
    #             on_next(470, 9),
    #             on_next(550, 10),
    #             on_completed(590)
    #     )

    #     var ys = scheduler.create_hot_observable(
    #             on_next(255, true),
    #             on_next(330, true),
    #             on_next(350, true),
    #             on_completed(400)
    #     )

    #     var res = scheduler.startWithCreate(function () {
    #         return xs.window(ys).select(function (w, i) {
    #             return w.select(function (x) {
    #                 return i.toString() + ' ' + x.toString()
    #             })
    #         }).mergeObservable()
    #     })

    #     res.messages.assert_equal(
    #             on_next(250, "0 3"),
    #             on_next(260, "1 4"),
    #             on_next(310, "1 5"),
    #             on_next(340, "2 6"),
    #             on_completed(400)
    #     )

    #     xs.subscriptions.assert_equal(
    #         subscribe(200, 400)
    #     )

    #     ys.subscriptions.assert_equal(
    #         subscribe(200, 400)
    #     )
    # })

    # def test_Window_Boundaries_on_errorSource():
    #     var ex = 'ex'
    #     var scheduler = TestScheduler()

    #     var xs = scheduler.create_hot_observable(
    #             on_next(90, 1),
    #             on_next(180, 2),
    #             on_next(250, 3),
    #             on_next(260, 4),
    #             on_next(310, 5),
    #             on_next(340, 6),
    #             on_next(380, 7),
    #             on_error(400, ex)
    #     )

    #     var ys = scheduler.create_hot_observable(
    #             on_next(255, true),
    #             on_next(330, true),
    #             on_next(350, true),
    #             on_completed(500)
    #     )

    #     var res = scheduler.startWithCreate(function () {
    #         return xs.window(ys).select(function (w, i) {
    #             return w.select(function (x) {
    #                 return i.toString() + ' ' + x.toString()
    #             })
    #         }).mergeObservable()
    #     })

    #     res.messages.assert_equal(
    #             on_next(250, "0 3"),
    #             on_next(260, "1 4"),
    #             on_next(310, "1 5"),
    #             on_next(340, "2 6"),
    #             on_next(380, "3 7"),
    #             on_error(400, ex)
    #     )

    #     xs.subscriptions.assert_equal(
    #         subscribe(200, 400)
    #     )

    #     ys.subscriptions.assert_equal(
    #         subscribe(200, 400)
    #     )
    # })

    # def test_Window_Boundaries_on_errorBoundaries():
    #     var ex = 'ex'
    #     var scheduler = TestScheduler()

    #     var xs = scheduler.create_hot_observable(
    #             on_next(90, 1),
    #             on_next(180, 2),
    #             on_next(250, 3),
    #             on_next(260, 4),
    #             on_next(310, 5),
    #             on_next(340, 6),
    #             on_next(410, 7),
    #             on_next(420, 8),
    #             on_next(470, 9),
    #             on_next(550, 10),
    #             on_completed(590)
    #     )

    #     var ys = scheduler.create_hot_observable(
    #             on_next(255, true),
    #             on_next(330, true),
    #             on_next(350, true),
    #             on_error(400, ex)
    #     )

    #     var res = scheduler.startWithCreate(function () {
    #         return xs.window(ys).select(function (w, i) {
    #             return w.select(function (x) {
    #                 return i.toString() + ' ' + x.toString()
    #             })
    #         }).mergeObservable()
    #     })

    #     res.messages.assert_equal(
    #             on_next(250, "0 3"),
    #             on_next(260, "1 4"),
    #             on_next(310, "1 5"),
    #             on_next(340, "2 6"),
    #             on_error(400, ex)
    #     )

    #     xs.subscriptions.assert_equal(
    #         subscribe(200, 400)
    #     )

    #     ys.subscriptions.assert_equal(
    #         subscribe(200, 400)
    #     )
    # })

if __name__ == '__main__':
    unittest.main()