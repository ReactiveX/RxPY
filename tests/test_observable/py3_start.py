import unittest
import rx
asyncio = rx.config['asyncio']
Future = rx.config['Future']

from rx import Observable
from rx.testing import TestScheduler, ReactiveTest

send = ReactiveTest.send
close = ReactiveTest.close
throw = ReactiveTest.throw
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestStart(unittest.TestCase):

    def test_start_async(self):
        loop = asyncio.get_event_loop()
        success = [False]

        @asyncio.coroutine
        def go():
            def func():
                future = Future()
                future.set_result(42)
                return future

            source = Observable.start_async(func)

            def send(x):
                success[0] = (42 == x)
            source.subscribe_callbacks(send)

        loop.run_until_complete(go())
        assert(all(success))

    def test_start_async_error(self):
        loop = asyncio.get_event_loop()
        success = [False]

        @asyncio.coroutine
        def go():
            def func():
                future = Future()
                future.set_exception(Exception(str(42)))
                return future

            source = Observable.start_async(func)

            def throw(ex):
                success[0] = (str(42) == str(ex))
            source.subscribe_callbacks(throw=throw)

        loop.run_until_complete(go())
        assert(all(success))

    def test_start_action2(self):
        scheduler = TestScheduler()

        done = [False]

        def create():
            def func():
                done[0] = True
            return Observable.start(func, scheduler)

        res = scheduler.start(create)

        assert res.messages == [
            send(200, None),
            close(200)]

        assert(done)


    def test_start_func2(self):
        scheduler = TestScheduler()

        def create():
            def func():
                return 1
            return Observable.start(func, scheduler)
        res = scheduler.start(create)

        assert res.messages == [
            send(200, 1),
            close(200)]

    def test_start_funcerror(self):
        ex = Exception()

        scheduler = TestScheduler()

        def create():
            def func():
                raise ex
            return Observable.start(func, scheduler)
        res = scheduler.start(create)

        assert res.messages == [
            throw(200, ex)]
