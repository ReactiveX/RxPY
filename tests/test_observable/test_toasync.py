import unittest

from rx.observable import Observable
from rx.testing import TestScheduler, ReactiveTest
from rx.disposables import Disposable, SerialDisposable

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created

class TestToAsync(unittest.TestCase):
    def test_to_async_context(self):
        class Context:
            def __init__(self):
                self.value = 42
            def func(self, x):
                return self.value + x

        scheduler = TestScheduler()

        def create():
            context = Context()
            return Observable.to_async(context.func, scheduler)(42)

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(200, 84),
            on_completed(200)
        )

    def test_to_async0(self):
        scheduler = TestScheduler()

        def create():
            def func():
                return 0

            return Observable.to_async(func, scheduler)()

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(200, 0),
            on_completed(200)
        )

    def test_to_async1(self):
        scheduler = TestScheduler()

        def create():
            def func(x):
                return x

            return Observable.to_async(func, scheduler)(1)

        res = scheduler.start(create)

        res.messages.assert_equal(
            on_next(200, 1),
            on_completed(200)
         )

    def test_to_async2(self):
        scheduler = TestScheduler()
    
        def create():
            def func(x, y):
                return x + y
        
            return Observable.to_async(func, scheduler)(1, 2)
      
        res = scheduler.start(create)
        
        res.messages.assert_equal(
            on_next(200, 3),
            on_completed(200)
        )

# def test_to_async3(self):
#   scheduler = TestScheduler()

#   res = scheduler.start(create)
#     return Observable.to_async(function (x, y, z) {
#       return x + y + z
#     }, null, scheduler)(1, 2, 3)
#   })

#   res.messages.assert_equal(
#     on_next(200, 6),
#     on_completed(200)
#   )
# })

# def test_to_async4(self):
#   scheduler = TestScheduler()

#   res = scheduler.start(create)
#     return Observable.to_async(function (a, b, c, d) {
#       return a + b + c + d
#     }, null, scheduler)(1, 2, 3, 4)
#   })

#   res.messages.assert_equal(
#     on_next(200, 10),
#     on_completed(200)
#   )
# })

# def test_to_async_Error0(self):
#   ex = Error()

#   scheduler = TestScheduler()

#   res = scheduler.start(create)
#     return Observable.to_async(function () {
#       throw ex
#     }, null, scheduler)()
#   })

#   res.messages.assert_equal(
#     onError(200, ex)
#   )
# })

# def test_to_async_Error1(self):
#   ex = Error()

#   scheduler = TestScheduler()

#   res = scheduler.start(create)
#     return Observable.to_async(function (a) {
#       throw ex
#     }, null, scheduler)(1)
#   })

#   res.messages.assert_equal(
#     onError(200, ex)
#   )
# })

# def test_to_async_Error2(self):
#   ex = Error();

#   scheduler = TestScheduler();

#   res = scheduler.start(create)
#     return Observable.to_async(function (a, b) {
#       throw ex;
#     }, null, scheduler)(1, 2);
#   });

#   res.messages.assert_equal(onError(200, ex));
# });

# def test_to_async_Error3(self):
#   ex = Error();

#   scheduler = TestScheduler();

#   res = scheduler.start(create)
#     return Observable.to_async(function (a, b, c) {
#       throw ex;
#     }, null, scheduler)(1, 2, 3);
#   });

#   res.messages.assert_equal(onError(200, ex));
# });

# def test_to_async_Error4(self):
#   ex = Error();

#   scheduler = TestScheduler();

#   res = scheduler.start(create)
#     return Observable.to_async(function (a, b, c, d) {
#       throw ex;
#     }, null, scheduler)(1, 2, 3, 4);
#   });

#   res.messages.assert_equal(
#     onError(200, ex)
#   );
# });