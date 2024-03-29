import asyncio
import unittest
from asyncio import Future

import reactivex
from reactivex.testing import ReactiveTest, TestScheduler

on_next = ReactiveTest.on_next
on_completed = ReactiveTest.on_completed
on_error = ReactiveTest.on_error
subscribe = ReactiveTest.subscribe
subscribed = ReactiveTest.subscribed
disposed = ReactiveTest.disposed
created = ReactiveTest.created


class TestStart(unittest.TestCase):
    def test_start_async(self):
        loop = asyncio.get_event_loop()
        success = [False]

        async def go():
            def func():
                future = Future()
                future.set_result(42)
                return future

            source = reactivex.start_async(func)

            def on_next(x):
                success[0] = 42 == x

            source.subscribe(on_next)

        loop.run_until_complete(go())
        assert all(success)

    def test_start_async_error(self):
        loop = asyncio.get_event_loop()
        success = [False]

        async def go():
            def func():
                future = Future()
                future.set_exception(Exception(str(42)))
                return future

            source = reactivex.start_async(func)

            def on_error(ex):
                success[0] = str(42) == str(ex)

            source.subscribe(on_error=on_error)

        loop.run_until_complete(go())
        assert all(success)

    def test_start_action2(self):
        scheduler = TestScheduler()

        done = [False]

        def create():
            def func():
                done[0] = True

            return reactivex.start(func, scheduler)

        res = scheduler.start(create)

        assert res.messages == [on_next(200, None), on_completed(200)]

        assert done

    def test_start_func2(self):
        scheduler = TestScheduler()

        def create():
            def func():
                return 1

            return reactivex.start(func, scheduler)

        res = scheduler.start(create)

        assert res.messages == [on_next(200, 1), on_completed(200)]

    def test_start_funcerror(self):
        ex = Exception()

        scheduler = TestScheduler()

        def create():
            def func():
                raise ex

            return reactivex.start(func, scheduler)

        res = scheduler.start(create)

        assert res.messages == [on_error(200, ex)]
